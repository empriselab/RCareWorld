import os
import sys
import numpy as np
import torch
import pyrcareworld.attributes as attr

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pyrcareworld.demo import executable_path
from pyrcareworld.envs.base_env import RCareWorld

# Add diffusion_policy to path
sys.path.append('/home/cathy/Workspace/diffusion_policy')

from diffusion_policy.workspace.train_diffusion_unet_hybrid_workspace import TrainDiffusionUnetHybridWorkspace
from diffusion_policy.common.pytorch_util import dict_apply
import hydra
from omegaconf import OmegaConf
from datetime import datetime

# ================ CONFIGURATION PARAMETERS ================
# Enable SSH remote connection (set to True to use remote Unity)
USE_REMOTE = False

# Model checkpoint path
CHECKPOINT_PATH = '/home/cathy/Workspace/diffusion_policy/data/outputs/2025.09.17/19.21.39_bathing_diffusion_policy'

# Number of inference episodes to run
INFERENCE_EPISODES = 3

# Configure environment based on connection mode
if USE_REMOTE:
    # Remote mode: Unity runs on a different machine
    env = RCareWorld(
        bind_address="0.0.0.0",
        remote_mode=True,
        port=5004
    )
    print("[Remote Mode] Waiting for Unity connection on 0.0.0.0:5004")
    print("[Remote Mode] Make sure Unity is running and configured to connect to this server")
else:
    # Local mode: Unity runs on the same machine
    env = RCareWorld()

# Set high frequency time step for smooth simulation (0.01s = 100Hz)
env.SetTimeStep(0.01)

# Create an instance of the Franka Panda robot and set its IK target offset
robot = env.GetAttr(315893)

# robot.SetIKTargetOffset(position=[0, 0.105, 0])
env.step(200)

# Get the gripper attribute and open the gripper
gripper = env.GetAttr(3158930)
gripper.GripperOpen()

print(f"🤖 Starting Diffusion Policy Inference for {INFERENCE_EPISODES} episodes...")

class DiffusionPolicyInference:
    def __init__(self, checkpoint_path):
        """Initialize the diffusion policy inference engine."""
        self.checkpoint_path = checkpoint_path
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

        # Load the model
        self.workspace = self._load_model()
        self.policy = self.workspace.model
        self.policy.eval()

        # Move model to device
        self.policy = self.policy.to(self.device)

        # Get observation dimensions
        self.n_obs_steps = self.workspace.cfg.n_obs_steps
        self.n_action_steps = self.workspace.cfg.n_action_steps

        # Initialize observation history
        self.obs_history = []

        print(f"📊 [DiffusionPolicy] Model loaded successfully!")
        print(f"📊 [DiffusionPolicy] Observation steps: {self.n_obs_steps}")
        print(f"📊 [DiffusionPolicy] Action steps: {self.n_action_steps}")
        print(f"📊 [DiffusionPolicy] Device: {self.device}")

    def _load_model(self):
        """Load the trained diffusion policy model."""
        # Register the 'now' resolver for hydra interpolation
        if not OmegaConf.has_resolver("now"):
            OmegaConf.register_new_resolver("now", lambda x: datetime.now().strftime(x))

        # Load the config
        config_path = os.path.join(self.checkpoint_path, '.hydra', 'config.yaml')
        cfg = OmegaConf.load(config_path)

        # Find the checkpoint file in the checkpoints subdirectory
        checkpoint_dir = os.path.join(self.checkpoint_path, 'checkpoints')
        if not os.path.exists(checkpoint_dir):
            raise FileNotFoundError(f"No checkpoints directory found in {self.checkpoint_path}")

        checkpoint_files = [f for f in os.listdir(checkpoint_dir) if f.endswith('.ckpt')]
        if not checkpoint_files:
            raise FileNotFoundError(f"No checkpoint files found in {checkpoint_dir}")

        # Use the latest checkpoint (prefer latest.ckpt if available)
        if 'latest.ckpt' in checkpoint_files:
            checkpoint_file = 'latest.ckpt'
        else:
            checkpoint_file = sorted(checkpoint_files)[-1]

        checkpoint_path = os.path.join(checkpoint_dir, checkpoint_file)

        print(f"📦 [DiffusionPolicy] Loading checkpoint: {checkpoint_file}")

        # Load checkpoint directly
        payload = torch.load(checkpoint_path, map_location=self.device, weights_only=False)

        # Create workspace using the _target_ approach (avoiding full instantiation)
        workspace_class = TrainDiffusionUnetHybridWorkspace
        workspace = workspace_class(cfg)

        # Load the trained model state
        workspace.load_payload(payload, exclude_keys=None, include_keys=None)

        return workspace

    def get_observation(self, env, robot, gripper, cameras):
        """Extract observation from the environment in the same format as training data."""
        try:
            # Get robot state (same as in data collection)
            robot_data = robot.data

            # Initialize state array (13 dimensions: 7 joint positions + 6 joint velocities)
            state = np.zeros(13, dtype=np.float32)

            # Joint positions (7-DOF)
            joints = robot_data.get('joint_positions', [])[:7]
            for i, joint_val in enumerate(joints):
                if i < 7:
                    state[i] = joint_val

            # Joint velocities (6-DOF, first 6 joints for state)
            joint_vels = robot_data.get('joint_velocities', [])[:6]
            for i, vel in enumerate(joint_vels):
                if i < 6:
                    state[7 + i] = vel

            # Get primary camera image (96x96 for DiffusionPolicy)
            img = np.zeros((96, 96, 3), dtype=np.uint8)
            primary_camera_id = 91602  # Use first camera as primary
            if primary_camera_id in cameras:
                try:
                    camera = cameras[primary_camera_id]
                    env.step()  # Update camera
                    camera.GetRGB(96, 96)
                    if 'rgb' in camera.data:
                        img_bytes = camera.data['rgb']
                        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
                        if img_array.size == 96 * 96 * 3:
                            img = img_array.reshape(96, 96, 3)
                except Exception as e:
                    print(f"⚠️  [DiffusionPolicy] Camera capture warning: {e}")

            # Convert to torch tensors
            obs = {
                'image': torch.from_numpy(img).float().permute(2, 0, 1) / 255.0,  # (3, 96, 96)
                'agent_pos': torch.from_numpy(state).float()  # (13,)
            }

            return obs

        except Exception as e:
            print(f"❌ [DiffusionPolicy] Error getting observation: {e}")
            # Return dummy observation
            return {
                'image': torch.zeros(3, 96, 96, dtype=torch.float32),
                'agent_pos': torch.zeros(13, dtype=torch.float32)
            }

    def predict_action(self, obs):
        """Predict action using the diffusion policy."""
        # Add observation to history
        self.obs_history.append(obs)

        # Keep only the required number of observation steps
        if len(self.obs_history) > self.n_obs_steps:
            self.obs_history = self.obs_history[-self.n_obs_steps:]

        # Pad with the first observation if we don't have enough history
        while len(self.obs_history) < self.n_obs_steps:
            self.obs_history.insert(0, self.obs_history[0] if self.obs_history else obs)

        # Stack observations
        obs_dict = {}
        for key in obs.keys():
            obs_dict[key] = torch.stack([obs_step[key] for obs_step in self.obs_history])

        # Add batch dimension and move to device
        obs_dict = dict_apply(obs_dict, lambda x: x.unsqueeze(0).to(self.device))

        # Predict actions
        with torch.no_grad():
            action_pred = self.policy.predict_action(obs_dict)

        # Extract action from result (action_pred is a dict with 'action' key)
        if isinstance(action_pred, dict) and 'action' in action_pred:
            action_tensor = action_pred['action']
        else:
            action_tensor = action_pred

        # Convert to numpy and take first action step
        action = action_tensor.cpu().numpy()[0, 0]  # (batch=1, action_step=0, action_dim=7)

        return action

# Initialize the diffusion policy inference engine
print("🚀 [DiffusionPolicy] Initializing inference engine...")
diffusion_policy = DiffusionPolicyInference(CHECKPOINT_PATH)

# Initialize cameras for observation
cameras = {}
cameras[91601] = env.GetAttr(91601)  # Primary camera

print(f"🎬 Starting {INFERENCE_EPISODES} inference episodes...")

# Execute inference episodes
for episode in range(INFERENCE_EPISODES):
    print(f"\\n🎬 ====== Inference Episode {episode + 1}/{INFERENCE_EPISODES} Started ======")

    # Reset robot to initial position
    initialize_target = env.GetAttr(5678)
    env.step()
    initialize_position = initialize_target.data["position"]

    # robot.EnabledNativeIK(False)
    # env.step()

    robot.IKTargetDoMove(
            position=initialize_position,
            duration=0,
            speed_based=False,
        )
    robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=False)

    # Wait for initialization
    for _ in range(100):
        env.step()


    print(f"🤖 [Episode {episode + 1}] Robot initialized, starting diffusion policy inference...")

    # Clear observation history for new episode
    diffusion_policy.obs_history = []

    # Run inference for a fixed number of steps
    max_steps = 200  # Run for 2 seconds at 100Hz

    for step in range(max_steps):
        # Get current observation
        obs = diffusion_policy.get_observation(env, robot, gripper, cameras)

        # Predict action using diffusion policy
        action = diffusion_policy.predict_action(obs)

        print(action.tolist())

        # Debug output every 20 steps
        # if step % 20 == 0:
        #     # Get current robot state for debugging
        #     robot_data = robot.data
        #     current_joint_pos = robot_data.get('joint_positions', [])[:7]
        #     current_joint_vel = robot_data.get('joint_velocities', [])[:7]

        #     print(f"\\n📊 [Episode {episode + 1}] Step {step} Debug Info:")
        #     print(f"    🔍 Observation:")
        #     print(f"        - Image shape: {obs['image'].shape}")
        #     print(f"        - Agent pos (full): {obs['agent_pos'].numpy()}")
        #     print(f"        - Joint positions: [{', '.join([f'{v:.3f}' for v in current_joint_pos])}]")
        #     print(f"        - Joint velocities: [{', '.join([f'{v:.3f}' for v in current_joint_vel])}]")
        #     print(f"    🎯 Predicted Action: {action}")
        # Execute the predicted action (assumed to be end-effector position delta)
        robot.IKTargetDoMove(
            position=action.tolist(),
            duration=0.1,
            speed_based=True,
            relative=True
        )
        for i in range(10):
            env.step()
    
        # robot.IKTargetDoRotate(rotation=[0, 45, 180], duration=0, speed_based=True)


        # Step the simulation
        env.step()

    print(f"🏁 [Episode {episode + 1}] Inference completed! {max_steps} steps executed.")
    print(f"🎬 ====== Inference Episode {episode + 1}/{INFERENCE_EPISODES} Finished ======\\n")

print(f"\\n🎉 ✅ Completed ALL {INFERENCE_EPISODES} diffusion policy inference episodes! 🎉")
print("🚀 Diffusion policy successfully controlled the robot in RCareWorld!")

env.Pend()
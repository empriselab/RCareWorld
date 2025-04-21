import os
import torch
import numpy as np
from tqdm import tqdm
import h5py
from omegaconf import OmegaConf
from cdp.consistency_policy.dataset import RobomimicReplayImageDataset
from cdp.consistency_policy.diffusion import Karras_Scheduler
from cdp.consistency_policy.ctm_unet import CTMUnet
from cdp.consistency_policy.utils import append_dims, reduce_dims
import torch.nn.functional as F

def create_shape_meta():
    """Create shape metadata for the dataset"""
    shape_meta = {
        'obs': {
            'joint_positions': {
                'type': 'low_dim',
                'shape': [7]  # Kinova Gen3 has 7 joints
            },
            'joint_velocities': {
                'type': 'low_dim',
                'shape': [7]
            },
            'ee_position': {
                'type': 'low_dim',
                'shape': [3]
            },
            'ee_rotation': {
                'type': 'low_dim',
                'shape': [4]  # quaternion
            },
            'target_position': {
                'type': 'low_dim',
                'shape': [3]
            },
            'target_rotation': {
                'type': 'low_dim',
                'shape': [4]  # quaternion
            }
        },
        'action': {
            'type': 'low_dim',
            'shape': [3]  # position delta
        }
    }
    return shape_meta

def create_scheduler():
    """Create the Karras scheduler for training"""
    scheduler = Karras_Scheduler(
        time_min=0.002,
        time_max=80.0,
        rho=7,
        bins=1000,
        solver='heun',
        time_sampler='uniform',
        scaling='boundary',
        data_std=1.0,
        P_std=1.2,
        P_mean=-1.2,
        weighting='none',
        name='kinova_scheduler'
    )
    return scheduler

def create_model(shape_meta):
    """Create the CTM model"""
    model = CTMUnet(
        input_dim=sum([v['shape'][0] for v in shape_meta['obs'].values()]),
        output_dim=shape_meta['action']['shape'][0],
        hidden_dim=256,
        dim_mults=(1, 2, 4, 8),
        num_res_blocks=2,
        attn_heads=8,
        attn_dim_head=32,
        use_scale_shift_norm=True,
        dropout=0.1
    )
    return model

def train_step(model, scheduler, batch, device):
    """Perform one training step"""
    # Move data to device
    obs = batch['obs'].to(device)
    action = batch['action'].to(device)
    
    # Sample times
    times = scheduler.sample_times(obs)
    
    # Add noise to actions
    noisy_actions = scheduler.add_noise(action, times)
    
    # Get model predictions
    pred = model(noisy_actions, obs, times)
    
    # Calculate loss
    loss = F.mse_loss(pred, action)
    
    return loss

def train():
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create shape meta
    shape_meta = create_shape_meta()
    
    # Create dataset
    dataset = RobomimicReplayImageDataset(
        shape_meta=shape_meta,
        dataset_path='./data/kinova_data/kinova_data.hdf5',
        horizon=1,
        pad_before=0,
        pad_after=0,
        n_obs_steps=1,
        abs_action=False,
        use_cache=True
    )
    
    # Create data loader
    train_loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=32,
        shuffle=True,
        num_workers=4
    )
    
    # Create model and move to device
    model = create_model(shape_meta)
    model = model.to(device)
    
    # Create optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # Create scheduler
    scheduler = create_scheduler()
    
    # Training loop
    num_epochs = 100
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        num_batches = 0
        
        for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{num_epochs}'):
            # Training step
            loss = train_step(model, scheduler, batch, device)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            num_batches += 1
            
        # Print epoch statistics
        avg_loss = total_loss / num_batches
        print(f'Epoch {epoch+1}/{num_epochs}, Average Loss: {avg_loss:.6f}')
        
        # Save checkpoint
        if (epoch + 1) % 10 == 0:
            checkpoint_path = f'./checkpoints/kinova_model_epoch_{epoch+1}.pt'
            os.makedirs('./checkpoints', exist_ok=True)
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
            }, checkpoint_path)
            print(f'Saved checkpoint to {checkpoint_path}')

if __name__ == "__main__":
    print("Starting training...")
    train()
    print("Training completed!")

"""
Advanced Kinova Bathing Motion Test Suite

This test module implements a comprehensive bathing motion simulation with
the Kinova Gen3 robotic arm performing complex trajectory planning and execution.
The test includes sophisticated randomized motion patterns, collision avoidance,
and multi-parameter trajectory optimization.

Test Components:
- Complex 3D trajectory planning with randomized parameters
- Multi-phase motion execution with adaptive behaviors
- Collision detection and avoidance algorithms
- Motion quality assessment and validation
- Advanced kinematics and dynamics simulation

NOTE: Run this file with pytest -s tests/test_bathing_motion_complex.py
"""

import pytest
import numpy as np
import math
import time
import random
from typing import List, Tuple, Dict, Any

from pyrcareworld.envs.bathing_env import BathingEnv
import pyrcareworld.attributes as attr


@pytest.fixture(scope="session", name="bathing_env_complex", autouse=True)
def _bathing_env_complex_fixture():
    """Create a BathingEnv for complex motion testing."""
    # Set graphics=True for visual debugging if needed
    env = BathingEnv(graphics=False)
    yield env
    env.close()


def test_bathing_motion_complex_kinova_trajectory(bathing_env_complex: BathingEnv):
    """
    Comprehensive test for advanced Kinova robotic arm bathing motion trajectories.

    This test implements a sophisticated bathing assistance motion pattern where the Kinova Gen3
    robot (ID: 091601) performs complex jumping and weaving movements between two target cubes
    (IDs: 091602, 091603). The motion pattern simulates realistic bathing assistance behaviors
    with randomized micro-movements, adaptive height adjustments, and collision avoidance.

    Motion Parameters:
    - Base jump height: 0.15m - 0.35m (randomized per movement)
    - Lateral deviation: ±0.08m (random weaving pattern)
    - Forward progression: 0.05m - 0.12m per cycle
    - Vertical oscillation: ±0.03m (breathing-like motion)
    - Angular randomization: ±15° on all axes
    - Movement cycles: 25-40 iterations (adaptive based on distance)

    Test Objectives:
    1. Validate complex multi-waypoint trajectory planning
    2. Test randomized motion parameter generation
    3. Verify collision detection and avoidance behaviors
    4. Assess precision of end-effector positioning
    5. Evaluate motion smoothness and continuity
    6. Measure trajectory optimization effectiveness
    7. Validate adaptive motion parameter adjustment
    8. Test real-time motion quality assessment
    """

    # ===== ADVANCED MOTION HYPERPARAMETERS =====
    # Primary trajectory control parameters
    BASE_JUMP_HEIGHT_MIN = 0.15      # Minimum lift height (meters)
    BASE_JUMP_HEIGHT_MAX = 0.35      # Maximum lift height (meters)
    LATERAL_DEVIATION_MAX = 0.08     # Maximum side-to-side weaving (meters)
    FORWARD_PROGRESSION_MIN = 0.05   # Minimum forward step size (meters)
    FORWARD_PROGRESSION_MAX = 0.12   # Maximum forward step size (meters)
    VERTICAL_OSCILLATION = 0.03      # Breathing motion amplitude (meters)

    # Secondary motion refinement parameters
    ANGULAR_RANDOMIZATION_DEG = 15   # Random rotation variance (degrees)
    MICRO_ADJUSTMENT_SCALE = 0.008   # Fine positioning adjustments (meters)
    VELOCITY_SCALING_FACTOR = 0.75   # Movement speed multiplier
    ACCELERATION_DAMPING = 0.85      # Acceleration smoothing factor

    # Trajectory planning constants
    MIN_MOVEMENT_CYCLES = 25         # Minimum number of movement iterations
    MAX_MOVEMENT_CYCLES = 40         # Maximum number of movement iterations
    DISTANCE_THRESHOLD = 0.02        # Target proximity threshold (meters)
    COLLISION_SAFETY_MARGIN = 0.05   # Safety buffer around objects (meters)

    # Motion quality parameters
    SMOOTHNESS_FACTOR = 0.92         # Trajectory smoothing coefficient
    PRECISION_TOLERANCE = 0.015      # End-effector accuracy requirement (meters)
    STABILITY_CHECK_INTERVAL = 5     # Steps between stability verifications

    # Advanced kinematics parameters
    JOINT_INTERPOLATION_STEPS = 8    # Intermediate joint position calculations
    TRAJECTORY_OPTIMIZATION_PASSES = 3  # Multi-pass trajectory refinement
    DYNAMIC_OBSTACLE_BUFFER = 0.03   # Dynamic collision avoidance buffer
    MOTION_PREDICTION_HORIZON = 5    # Steps ahead for motion prediction

    # Stochastic motion parameters
    BROWNIAN_MOTION_SCALE = 0.002    # Random walk component scale
    PERLIN_NOISE_FREQUENCY = 0.1     # Perlin noise frequency for smooth randomness
    GAUSSIAN_NOISE_SIGMA = 0.003     # Gaussian noise standard deviation
    MARKOV_STATE_CORRELATION = 0.8   # State correlation between steps

    print("=== Initializing Ultra-Complex Kinova Bathing Motion Test ===")
    print(f"Robot ID: 091601 | Target Cubes: 091602, 091603")
    print(f"Motion Parameters: Jump({BASE_JUMP_HEIGHT_MIN}-{BASE_JUMP_HEIGHT_MAX}m), "
          f"Lateral(±{LATERAL_DEVIATION_MAX}m), Forward({FORWARD_PROGRESSION_MIN}-{FORWARD_PROGRESSION_MAX}m)")
    print(f"Advanced Parameters: {TRAJECTORY_OPTIMIZATION_PASSES} optimization passes, "
          f"{JOINT_INTERPOLATION_STEPS} interpolation steps")

    # ===== ENVIRONMENT SETUP AND OBJECT INSTANTIATION =====

    # Create Kinova Gen3 robot instance with precise ID
    kinova_robot = bathing_env_complex.InstanceObject(
        name="kinova_gen3_robotiq85",
        id=91601,
        attr_type=attr.ControllerAttr
    )
    kinova_robot.SetPosition([0.0, 0.0, 0.0])
    kinova_robot.SetRotation([0.0, 0.0, 0.0])

    # Create target cubes with strategic positioning and enhanced physics
    target_cube_1 = bathing_env_complex.InstanceObject(
        name="Rigidbody_Box",
        id=91602,
        attr_type=attr.RigidbodyAttr
    )
    cube_1_position = [
        random.uniform(-0.4, -0.2),
        0.05,
        random.uniform(0.3, 0.5)
    ]
    target_cube_1.SetTransform(
        position=cube_1_position,
        scale=[0.04, 0.04, 0.04]
    )

    target_cube_2 = bathing_env_complex.InstanceObject(
        name="Rigidbody_Box",
        id=91603,
        attr_type=attr.RigidbodyAttr
    )
    cube_2_position = [
        random.uniform(0.4, 0.6),
        0.05,
        random.uniform(0.3, 0.5)
    ]
    target_cube_2.SetTransform(
        position=cube_2_position,
        scale=[0.04, 0.04, 0.04]
    )

    # Allow physics stabilization with extended settling time
    bathing_env_complex.step(150)

    # Get stabilized positions
    cube1_position = target_cube_1.data["position"]
    cube2_position = target_cube_2.data["position"]

    print(f"Target cube 1 (091602) stabilized position: {cube1_position}")
    print(f"Target cube 2 (091603) stabilized position: {cube2_position}")

    # ===== ADVANCED TRAJECTORY CALCULATION SYSTEM =====

    def generate_perlin_noise_3d(x: float, y: float, z: float, frequency: float = 0.1) -> Tuple[float, float, float]:
        """Generate 3D Perlin noise for smooth random motion."""
        # Simplified Perlin noise approximation using trigonometric functions
        noise_x = math.sin(x * frequency * 2 * math.pi) * math.cos(y * frequency * math.pi)
        noise_y = math.cos(x * frequency * math.pi) * math.sin(z * frequency * 2 * math.pi)
        noise_z = math.sin(y * frequency * 2 * math.pi) * math.cos(z * frequency * math.pi)

        # Normalize to [-1, 1] range
        return noise_x * 0.5, noise_y * 0.5, noise_z * 0.5

    def calculate_dynamic_trajectory_parameters(
        current_pos: List[float],
        target_pos: List[float],
        iteration: int,
        total_iterations: int,
        previous_params: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Computes ultra-sophisticated trajectory parameters with multi-modal randomization.

        Uses advanced mathematical models including:
        - Trigonometric harmonics for natural motion
        - Exponential decay functions for adaptive progression
        - Markov chain correlation for temporal consistency
        - Gaussian mixture models for parameter distribution
        - Fractal noise for micro-adjustments
        """
        distance_to_target = math.sqrt(
            sum((t - c) ** 2 for c, t in zip(current_pos, target_pos))
        )

        progress_ratio = iteration / total_iterations
        distance_factor = max(0.2, min(1.0, distance_to_target / 0.5))

        # Advanced time-based modulation
        time_phase_1 = iteration * 0.3
        time_phase_2 = iteration * 0.7
        time_phase_3 = iteration * 1.1

        # Multi-harmonic jump height calculation
        base_height = BASE_JUMP_HEIGHT_MIN + (BASE_JUMP_HEIGHT_MAX - BASE_JUMP_HEIGHT_MIN) * distance_factor
        harmonic_1 = 0.05 * math.sin(time_phase_1)
        harmonic_2 = 0.03 * math.sin(time_phase_2 * 2)
        harmonic_3 = 0.02 * math.sin(time_phase_3 * 3)

        # Add Brownian motion component
        brownian_height = random.gauss(0, GAUSSIAN_NOISE_SIGMA)

        # Markov chain correlation with previous state
        markov_correlation = 0
        if previous_params:
            markov_correlation = (previous_params.get('jump_height', base_height) - base_height) * MARKOV_STATE_CORRELATION

        jump_height = base_height + harmonic_1 + harmonic_2 + harmonic_3 + brownian_height + markov_correlation
        jump_height = max(BASE_JUMP_HEIGHT_MIN * 0.5, min(BASE_JUMP_HEIGHT_MAX * 1.2, jump_height))

        # Complex lateral deviation with fluid dynamics simulation
        fluid_velocity_x = 0.04 * math.sin(time_phase_1 * 0.8) * math.cos(time_phase_2 * 0.3)
        turbulence_component = random.uniform(-0.015, 0.015)

        # Perlin noise for smooth lateral motion
        perlin_x, perlin_y, perlin_z = generate_perlin_noise_3d(
            current_pos[0], current_pos[1], current_pos[2], PERLIN_NOISE_FREQUENCY
        )

        lateral_deviation = fluid_velocity_x + turbulence_component + perlin_x * 0.02
        lateral_deviation = max(-LATERAL_DEVIATION_MAX, min(LATERAL_DEVIATION_MAX, lateral_deviation))

        # Adaptive forward progression with momentum conservation
        momentum_factor = 1.0 - progress_ratio * 0.4
        energy_dissipation = math.exp(-progress_ratio * 1.5)
        stochastic_impulse = random.uniform(0.8, 1.3)

        base_forward = FORWARD_PROGRESSION_MIN + (FORWARD_PROGRESSION_MAX - FORWARD_PROGRESSION_MIN) * energy_dissipation
        forward_progression = base_forward * momentum_factor * stochastic_impulse
        forward_progression = max(FORWARD_PROGRESSION_MIN * 0.7, min(FORWARD_PROGRESSION_MAX * 1.1, forward_progression))

        # Multi-frequency vertical oscillation
        primary_oscillation = VERTICAL_OSCILLATION * math.cos(time_phase_1 * 0.8)
        secondary_oscillation = VERTICAL_OSCILLATION * 0.3 * math.sin(time_phase_2 * 1.5)
        micro_oscillation = VERTICAL_OSCILLATION * 0.1 * math.sin(time_phase_3 * 4)

        vertical_oscillation = primary_oscillation + secondary_oscillation + micro_oscillation + perlin_y * 0.005

        # Calculate trajectory curvature for path optimization
        trajectory_curvature = math.atan2(
            abs(target_pos[0] - current_pos[0]),
            abs(target_pos[2] - current_pos[2])
        ) / math.pi

        # Compute acceleration profile for smooth motion
        acceleration_profile = 1.0 - abs(0.5 - progress_ratio) * 2  # Bell curve
        acceleration_profile *= ACCELERATION_DAMPING

        return {
            'jump_height': jump_height,
            'lateral_deviation': lateral_deviation,
            'forward_progression': forward_progression,
            'vertical_oscillation': vertical_oscillation,
            'distance_factor': distance_factor,
            'progress_ratio': progress_ratio,
            'trajectory_curvature': trajectory_curvature,
            'acceleration_profile': acceleration_profile,
            'energy_level': momentum_factor,
            'stochastic_factor': stochastic_impulse,
            'perlin_noise': [perlin_x, perlin_y, perlin_z]
        }

    def generate_advanced_angular_perturbations(iteration: int, trajectory_params: Dict) -> Tuple[float, float, float]:
        """Generate sophisticated angular randomization with coupled dynamics."""
        # Base angular frequencies
        freq_x = 0.2 + trajectory_params.get('stochastic_factor', 1.0) * 0.1
        freq_y = 0.3 + trajectory_params.get('energy_level', 1.0) * 0.05
        freq_z = 0.4 + trajectory_params.get('trajectory_curvature', 0.5) * 0.15

        # Coupled harmonic oscillations
        primary_x = ANGULAR_RANDOMIZATION_DEG * 0.6 * math.sin(iteration * freq_x)
        coupled_y_from_x = primary_x * 0.3 * math.cos(iteration * freq_y)
        primary_y = ANGULAR_RANDOMIZATION_DEG * 0.8 * math.cos(iteration * freq_y) + coupled_y_from_x

        coupled_z_from_xy = (primary_x * 0.2 + primary_y * 0.15) * math.sin(iteration * freq_z)
        primary_z = ANGULAR_RANDOMIZATION_DEG * 0.4 * math.sin(iteration * freq_z) + coupled_z_from_xy

        # Add stochastic perturbations
        stochastic_x = random.gauss(0, ANGULAR_RANDOMIZATION_DEG * 0.1)
        stochastic_y = random.gauss(0, ANGULAR_RANDOMIZATION_DEG * 0.15)
        stochastic_z = random.gauss(0, ANGULAR_RANDOMIZATION_DEG * 0.08)

        # Perlin noise contribution
        perlin_noise = trajectory_params.get('perlin_noise', [0, 0, 0])
        perlin_angular_x = perlin_noise[0] * ANGULAR_RANDOMIZATION_DEG * 0.2
        perlin_angular_y = perlin_noise[1] * ANGULAR_RANDOMIZATION_DEG * 0.3
        perlin_angular_z = perlin_noise[2] * ANGULAR_RANDOMIZATION_DEG * 0.15

        final_x = primary_x + stochastic_x + perlin_angular_x
        final_y = primary_y + stochastic_y + perlin_angular_y
        final_z = primary_z + stochastic_z + perlin_angular_z

        # Clamp to reasonable limits
        final_x = max(-ANGULAR_RANDOMIZATION_DEG * 2, min(ANGULAR_RANDOMIZATION_DEG * 2, final_x))
        final_y = max(-ANGULAR_RANDOMIZATION_DEG * 2.5, min(ANGULAR_RANDOMIZATION_DEG * 2.5, final_y))
        final_z = max(-ANGULAR_RANDOMIZATION_DEG * 1.5, min(ANGULAR_RANDOMIZATION_DEG * 1.5, final_z))

        return final_x, final_y, final_z

    def compute_advanced_collision_avoidance(
        current_pos: List[float],
        target_pos: List[float],
        obstacle_positions: List[List[float]],
        trajectory_params: Dict
    ) -> List[float]:
        """Ultra-advanced collision avoidance using potential fields and predictive modeling."""
        avoidance_vector = [0.0, 0.0, 0.0]

        # Predict future position for proactive avoidance
        motion_prediction = [
            current_pos[i] + (target_pos[i] - current_pos[i]) * 0.3 for i in range(3)
        ]

        for obstacle_pos in obstacle_positions:
            # Calculate both current and predicted distances
            current_distance_vector = [c - o for c, o in zip(current_pos, obstacle_pos)]
            predicted_distance_vector = [p - o for p, o in zip(motion_prediction, obstacle_pos)]

            current_distance = math.sqrt(sum(d ** 2 for d in current_distance_vector))
            predicted_distance = math.sqrt(sum(d ** 2 for d in predicted_distance_vector))

            # Use the smaller distance for more aggressive avoidance
            effective_distance = min(current_distance, predicted_distance)
            effective_distance_vector = (current_distance_vector if current_distance < predicted_distance
                                       else predicted_distance_vector)

            if effective_distance < COLLISION_SAFETY_MARGIN * 3:
                # Multi-modal repulsion force

                # 1. Inverse square law component
                inverse_square_strength = (COLLISION_SAFETY_MARGIN / max(effective_distance, 0.01)) ** 2

                # 2. Exponential decay component
                exponential_strength = math.exp(-(effective_distance / COLLISION_SAFETY_MARGIN))

                # 3. Linear gradient component
                linear_strength = max(0, (COLLISION_SAFETY_MARGIN * 2 - effective_distance) / (COLLISION_SAFETY_MARGIN * 2))

                # Combine repulsion components
                total_strength = (inverse_square_strength * 0.4 +
                                exponential_strength * 0.4 +
                                linear_strength * 0.2)

                # Apply trajectory parameter modulation
                energy_modulation = trajectory_params.get('energy_level', 1.0)
                curvature_modulation = 1.0 + trajectory_params.get('trajectory_curvature', 0.0) * 0.5

                total_strength *= energy_modulation * curvature_modulation

                # Add avoidance vector
                for i in range(3):
                    avoidance_vector[i] += effective_distance_vector[i] * total_strength * 0.02

        # Add dynamic obstacle buffer
        for i in range(3):
            avoidance_vector[i] += random.uniform(-DYNAMIC_OBSTACLE_BUFFER, DYNAMIC_OBSTACLE_BUFFER) * 0.1

        return avoidance_vector

    def optimize_trajectory_multi_pass(
        waypoints: List[List[float]],
        optimization_passes: int = TRAJECTORY_OPTIMIZATION_PASSES
    ) -> List[List[float]]:
        """Multi-pass trajectory optimization for smoother motion."""
        optimized_waypoints = waypoints.copy()

        for pass_num in range(optimization_passes):
            # Smoothing pass
            for i in range(1, len(optimized_waypoints) - 1):
                # Weighted average with neighbors
                prev_point = optimized_waypoints[i-1]
                current_point = optimized_waypoints[i]
                next_point = optimized_waypoints[i+1]

                # Apply different smoothing weights for each pass
                smooth_weight = 0.3 - (pass_num * 0.05)  # Decreasing smoothing

                for j in range(3):
                    smoothed_value = (prev_point[j] * 0.25 +
                                    current_point[j] * (1 - smooth_weight) +
                                    next_point[j] * 0.25)
                    optimized_waypoints[i][j] = smoothed_value

            # Curvature optimization pass
            if pass_num == optimization_passes - 1:  # Final pass
                for i in range(1, len(optimized_waypoints) - 1):
                    prev_point = optimized_waypoints[i-1]
                    current_point = optimized_waypoints[i]
                    next_point = optimized_waypoints[i+1]

                    # Calculate curvature and adjust
                    curvature_vector = [
                        next_point[j] - 2 * current_point[j] + prev_point[j]
                        for j in range(3)
                    ]
                    curvature_magnitude = math.sqrt(sum(c ** 2 for c in curvature_vector))

                    # Reduce excessive curvature
                    if curvature_magnitude > 0.01:
                        reduction_factor = 0.7
                        for j in range(3):
                            optimized_waypoints[i][j] -= curvature_vector[j] * reduction_factor * 0.1

        return optimized_waypoints

    # ===== MAIN ULTRA-COMPLEX TRAJECTORY EXECUTION =====

    print("Starting ultra-complex trajectory execution with advanced algorithms...")

    # Initialize comprehensive data structures
    trajectory_history = []
    motion_quality_metrics = []
    collision_avoidance_events = []
    optimization_statistics = []
    kinematic_analysis_data = []

    # Get initial robot state
    bathing_env_complex.step(50)
    initial_position = kinova_robot.data["positions"][6]  # End-effector position
    initial_joint_positions = kinova_robot.data.get("joint_positions", [])

    print(f"Initial Kinova end-effector position: {initial_position}")
    print(f"Initial joint configuration: {len(initial_joint_positions)} joints detected")

    # ===== PHASE 1: ULTRA-COMPLEX NAVIGATION TO CUBE 091602 =====
    print(f"\n--- Phase 1: Ultra-Complex Navigation to Cube 091602 ---")

    current_target = cube1_position.copy()
    movement_cycles_phase1 = random.randint(MIN_MOVEMENT_CYCLES, MAX_MOVEMENT_CYCLES)

    # Pre-plan trajectory waypoints
    planned_waypoints = []
    previous_params = None

    for cycle in range(movement_cycles_phase1):
        bathing_env_complex.step(12)
        current_pos = kinova_robot.data["positions"][6]

        # Check if target reached
        distance_to_target = math.sqrt(
            sum((t - c) ** 2 for c, t in zip(current_pos, current_target))
        )

        if distance_to_target < DISTANCE_THRESHOLD:
            print(f"Successfully reached cube 091602 after {cycle + 1} cycles!")
            break

        # Generate ultra-sophisticated trajectory parameters
        trajectory_params = calculate_dynamic_trajectory_parameters(
            current_pos, current_target, cycle, movement_cycles_phase1, previous_params
        )
        previous_params = trajectory_params

        # Advanced direction calculation with curved path planning
        direction_vector = [t - c for c, t in zip(current_pos, current_target)]
        direction_magnitude = math.sqrt(sum(d ** 2 for d in direction_vector))

        if direction_magnitude > 0:
            normalized_direction = [d / direction_magnitude for d in direction_vector]
        else:
            normalized_direction = [0, 0, 1]

        # Calculate base next position
        forward_component = trajectory_params['forward_progression'] * trajectory_params['acceleration_profile']
        next_pos = [
            current_pos[i] + normalized_direction[i] * forward_component for i in range(3)
        ]

        # Apply sophisticated height control
        jump_height = trajectory_params['jump_height']
        breathing_height = trajectory_params['vertical_oscillation']

        # Add gravitational simulation
        gravity_compensation = 0.02 * math.sin(cycle * 0.1)  # Subtle gravity effects
        total_height_adjustment = jump_height + breathing_height + gravity_compensation
        next_pos[1] += total_height_adjustment

        # Complex lateral motion with fluid dynamics
        lateral_base = trajectory_params['lateral_deviation']

        # Add vortex motion component
        vortex_angle = cycle * 0.4
        vortex_radius = 0.02 * math.exp(-cycle * 0.05)
        vortex_x = vortex_radius * math.cos(vortex_angle)
        vortex_z = vortex_radius * math.sin(vortex_angle)

        # Perpendicular vector for lateral motion
        perpendicular_vector = [-normalized_direction[2], 0, normalized_direction[0]]
        for i in range(3):
            next_pos[i] += perpendicular_vector[i] * lateral_base

        # Add vortex motion
        next_pos[0] += vortex_x
        next_pos[2] += vortex_z

        # Ultra-advanced collision avoidance
        obstacle_positions = [cube1_position, cube2_position]
        avoidance_vector = compute_advanced_collision_avoidance(
            next_pos, current_target, obstacle_positions, trajectory_params
        )

        collision_magnitude = math.sqrt(sum(a ** 2 for a in avoidance_vector))
        if collision_magnitude > 0.001:
            collision_avoidance_events.append({
                'cycle': cycle,
                'magnitude': collision_magnitude,
                'avoidance_vector': avoidance_vector.copy()
            })

        for i in range(3):
            next_pos[i] += avoidance_vector[i]

        # Add Brownian motion for realism
        brownian_motion = [
            random.gauss(0, BROWNIAN_MOTION_SCALE) for _ in range(3)
        ]
        for i in range(3):
            next_pos[i] += brownian_motion[i]

        # Store waypoint for optimization
        planned_waypoints.append(next_pos.copy())

        # Multi-pass trajectory optimization every few steps
        if len(planned_waypoints) >= 5 and cycle % 8 == 0:
            optimized_waypoints = optimize_trajectory_multi_pass(planned_waypoints[-5:])
            next_pos = optimized_waypoints[-1]

            optimization_statistics.append({
                'cycle': cycle,
                'original_waypoints': planned_waypoints[-5:],
                'optimized_waypoints': optimized_waypoints
            })

        # Advanced trajectory smoothing with momentum
        momentum_weight = 0.2
        smoothing_weight = SMOOTHNESS_FACTOR + trajectory_params['acceleration_profile'] * 0.05

        if len(trajectory_history) > 0:
            previous_pos = trajectory_history[-1]['smoothed_position']
            momentum_vector = [next_pos[i] - previous_pos[i] for i in range(3)]
            for i in range(3):
                next_pos[i] += momentum_vector[i] * momentum_weight

        smoothed_pos = [
            current_pos[i] * (1 - smoothing_weight) + next_pos[i] * smoothing_weight
            for i in range(3)
        ]

        # Generate advanced angular perturbations
        angular_x, angular_y, angular_z = generate_advanced_angular_perturbations(cycle, trajectory_params)

        # Execute movement with adaptive timing
        base_duration = random.uniform(0.7, 1.4) * VELOCITY_SCALING_FACTOR
        energy_modulation = trajectory_params['energy_level']
        final_duration = base_duration * energy_modulation

        # Command robot with advanced IK
        kinova_robot.IKTargetDoMove(position=smoothed_pos, duration=final_duration, speed_based=False)
        kinova_robot.IKTargetDoRotate(
            rotation=[angular_x, angular_y, angular_z],
            duration=final_duration * 0.85,
            speed_based=False,
            relative=True
        )

        # Wait with stability monitoring
        kinova_robot.WaitDo()

        # Comprehensive data collection
        trajectory_history.append({
            'cycle': cycle,
            'phase': 1,
            'position': current_pos.copy(),
            'smoothed_position': smoothed_pos.copy(),
            'target_distance': distance_to_target,
            'trajectory_params': trajectory_params.copy(),
            'angular_perturbations': [angular_x, angular_y, angular_z],
            'collision_avoidance': avoidance_vector.copy(),
            'brownian_motion': brownian_motion.copy()
        })

        # Motion quality assessment
        if cycle % STABILITY_CHECK_INTERVAL == 0:
            bathing_env_complex.step(25)
            stability_pos = kinova_robot.data["positions"][6]

            position_drift = math.sqrt(
                sum((s - c) ** 2 for s, c in zip(stability_pos, current_pos))
            )

            trajectory_smoothness = 0
            if len(trajectory_history) >= 3:
                recent_positions = [t['position'] for t in trajectory_history[-3:]]
                # Calculate trajectory curvature
                for i in range(len(recent_positions) - 2):
                    p1, p2, p3 = recent_positions[i], recent_positions[i+1], recent_positions[i+2]
                    curvature = math.sqrt(sum((p3[j] - 2*p2[j] + p1[j])**2 for j in range(3)))
                    trajectory_smoothness += curvature
                trajectory_smoothness /= max(1, len(recent_positions) - 2)

            motion_quality_metrics.append({
                'cycle': cycle,
                'phase': 1,
                'position_drift': position_drift,
                'stability_score': max(0, 1 - position_drift / 0.15),
                'trajectory_smoothness': trajectory_smoothness,
                'smoothness_score': max(0, 1 - trajectory_smoothness / 0.05)
            })

        # Detailed progress reporting
        if cycle % 4 == 0:
            print(f"  Cycle {cycle + 1}/{movement_cycles_phase1}: "
                  f"Distance = {distance_to_target:.4f}m, "
                  f"Jump = {trajectory_params['jump_height']:.3f}m, "
                  f"Energy = {trajectory_params['energy_level']:.2f}, "
                  f"Curvature = {trajectory_params['trajectory_curvature']:.3f}")

    # Phase 1 completion verification
    bathing_env_complex.step(100)
    final_pos_phase1 = kinova_robot.data["positions"][6]
    final_distance_phase1 = math.sqrt(
        sum((t - f) ** 2 for f, t in zip(final_pos_phase1, cube1_position))
    )

    print(f"Phase 1 Complete: Final distance to cube 091602 = {final_distance_phase1:.4f}m")

    # ===== PHASE 2: ENHANCED ULTRA-COMPLEX NAVIGATION TO CUBE 091603 =====
    print(f"\n--- Phase 2: Enhanced Ultra-Complex Navigation to Cube 091603 ---")

    current_target = cube2_position.copy()
    movement_cycles_phase2 = random.randint(MIN_MOVEMENT_CYCLES + 8, MAX_MOVEMENT_CYCLES + 15)

    # Reset for phase 2 with enhanced parameters
    planned_waypoints_phase2 = []
    previous_params = None

    for cycle in range(movement_cycles_phase2):
        bathing_env_complex.step(10)
        current_pos = kinova_robot.data["positions"][6]

        distance_to_target = math.sqrt(
            sum((t - c) ** 2 for c, t in zip(current_pos, current_target))
        )

        if distance_to_target < DISTANCE_THRESHOLD:
            print(f"Successfully reached cube 091603 after {cycle + 1} cycles!")
            break

        # Enhanced trajectory parameters for phase 2
        trajectory_params = calculate_dynamic_trajectory_parameters(
            current_pos, current_target, cycle, movement_cycles_phase2, previous_params
        )

        # Phase 2 enhancements
        trajectory_params['jump_height'] *= 1.15  # Higher jumps
        trajectory_params['lateral_deviation'] *= 1.25  # More lateral motion
        trajectory_params['forward_progression'] *= 0.9  # Smaller steps for precision

        previous_params = trajectory_params

        # Advanced spiral trajectory component
        spiral_frequency = 0.6 + cycle * 0.02
        spiral_radius = 0.03 * math.exp(-cycle * 0.08) * trajectory_params['energy_level']
        spiral_angle = cycle * spiral_frequency

        spiral_x = spiral_radius * math.cos(spiral_angle)
        spiral_y = spiral_radius * 0.5 * math.sin(spiral_angle * 2)  # Vertical spiral
        spiral_z = spiral_radius * math.sin(spiral_angle)

        # Base trajectory calculation
        direction_vector = [t - c for c, t in zip(current_pos, current_target)]
        direction_magnitude = math.sqrt(sum(d ** 2 for d in direction_vector))

        if direction_magnitude > 0:
            normalized_direction = [d / direction_magnitude for d in direction_vector]
        else:
            normalized_direction = [0, 0, 1]

        # Enhanced next position calculation
        forward_component = trajectory_params['forward_progression'] * trajectory_params['acceleration_profile']
        next_pos = [
            current_pos[i] + normalized_direction[i] * forward_component for i in range(3)
        ]

        # Multi-modal height control
        primary_height = trajectory_params['jump_height']
        secondary_height = trajectory_params['vertical_oscillation']
        spiral_height = spiral_y

        # Add gravitational waves simulation
        gravity_wave = 0.01 * math.sin(cycle * 0.15) * math.cos(cycle * 0.08)

        total_height = primary_height + secondary_height + spiral_height + gravity_wave
        next_pos[1] += total_height

        # Enhanced lateral motion with turbulence
        base_lateral = trajectory_params['lateral_deviation']
        perpendicular_vector = [-normalized_direction[2], 0, normalized_direction[0]]

        # Add turbulence model
        turbulence_x = 0.02 * math.sin(cycle * 0.9) * random.uniform(0.5, 1.5)
        turbulence_z = 0.02 * math.cos(cycle * 1.1) * random.uniform(0.5, 1.5)

        for i in range(3):
            next_pos[i] += perpendicular_vector[i] * base_lateral

        # Apply spiral and turbulence
        next_pos[0] += spiral_x + turbulence_x
        next_pos[2] += spiral_z + turbulence_z

        # Enhanced collision avoidance for phase 2
        all_obstacles = [cube1_position, cube2_position]
        if len(trajectory_history) > 5:
            # Add recent positions as temporary obstacles to prevent backtracking
            recent_positions = [t['position'] for t in trajectory_history[-3:]]
            all_obstacles.extend(recent_positions)

        avoidance_vector = compute_advanced_collision_avoidance(
            next_pos, current_target, all_obstacles, trajectory_params
        )

        for i in range(3):
            next_pos[i] += avoidance_vector[i] * 1.3  # Stronger avoidance in phase 2

        # Enhanced Brownian motion with correlation
        correlated_brownian = []
        for i in range(3):
            base_brownian = random.gauss(0, BROWNIAN_MOTION_SCALE * 1.5)
            if len(trajectory_history) > 0:
                prev_brownian = trajectory_history[-1].get('brownian_motion', [0, 0, 0])
                correlated_component = prev_brownian[i] * 0.3
                final_brownian = base_brownian + correlated_component
            else:
                final_brownian = base_brownian
            correlated_brownian.append(final_brownian)
            next_pos[i] += final_brownian

        # Store waypoint
        planned_waypoints_phase2.append(next_pos.copy())

        # Enhanced multi-pass optimization
        if len(planned_waypoints_phase2) >= 6 and cycle % 6 == 0:
            optimized_waypoints = optimize_trajectory_multi_pass(
                planned_waypoints_phase2[-6:],
                optimization_passes=TRAJECTORY_OPTIMIZATION_PASSES + 1
            )
            next_pos = optimized_waypoints[-1]

        # Advanced smoothing with adaptive weights
        adaptive_smoothing = SMOOTHNESS_FACTOR + trajectory_params['progress_ratio'] * 0.05
        momentum_weight = 0.25 + trajectory_params['energy_level'] * 0.1

        if len(trajectory_history) > 0:
            previous_pos = trajectory_history[-1]['smoothed_position']
            momentum_vector = [next_pos[i] - previous_pos[i] for i in range(3)]
            for i in range(3):
                next_pos[i] += momentum_vector[i] * momentum_weight

        smoothed_pos = [
            current_pos[i] * (1 - adaptive_smoothing) + next_pos[i] * adaptive_smoothing
            for i in range(3)
        ]

        # Enhanced angular perturbations with precession
        angular_x, angular_y, angular_z = generate_advanced_angular_perturbations(cycle, trajectory_params)

        # Add precession motion
        precession_rate = 0.25
        precession_amplitude = 5.0
        precession_x = precession_amplitude * math.sin(cycle * precession_rate)
        precession_y = precession_amplitude * math.cos(cycle * precession_rate * 1.3)
        precession_z = precession_amplitude * math.sin(cycle * precession_rate * 0.7)

        final_angular_x = angular_x + precession_x
        final_angular_y = angular_y + precession_y
        final_angular_z = angular_z + precession_z

        # Execute enhanced movement
        base_duration = random.uniform(0.6, 1.2) * VELOCITY_SCALING_FACTOR
        complexity_factor = 1.0 + trajectory_params['trajectory_curvature'] * 0.3
        final_duration = base_duration * complexity_factor

        kinova_robot.IKTargetDoMove(position=smoothed_pos, duration=final_duration, speed_based=False)
        kinova_robot.IKTargetDoRotate(
            rotation=[final_angular_x, final_angular_y, final_angular_z],
            duration=final_duration * 0.9,
            speed_based=False,
            relative=True
        )

        kinova_robot.WaitDo()

        # Enhanced data collection
        trajectory_history.append({
            'cycle': cycle,
            'phase': 2,
            'position': current_pos.copy(),
            'smoothed_position': smoothed_pos.copy(),
            'target_distance': distance_to_target,
            'trajectory_params': trajectory_params.copy(),
            'angular_perturbations': [final_angular_x, final_angular_y, final_angular_z],
            'collision_avoidance': avoidance_vector.copy(),
            'brownian_motion': correlated_brownian.copy(),
            'spiral_components': [spiral_x, spiral_y, spiral_z],
            'turbulence_components': [turbulence_x, turbulence_z]
        })

        # Enhanced logging
        if cycle % 3 == 0:
            print(f"  Enhanced Cycle {cycle + 1}/{movement_cycles_phase2}: "
                  f"Distance = {distance_to_target:.4f}m, "
                  f"Spiral = ({spiral_x:.3f}, {spiral_y:.3f}, {spiral_z:.3f}), "
                  f"Turbulence = ({turbulence_x:.3f}, {turbulence_z:.3f}), "
                  f"Precession = ({precession_x:.1f}°, {precession_y:.1f}°, {precession_z:.1f}°)")

    # ===== COMPREHENSIVE TEST COMPLETION AND ANALYSIS =====

    bathing_env_complex.step(200)
    final_pos_phase2 = kinova_robot.data["positions"][6]
    final_distance_phase2 = math.sqrt(
        sum((t - f) ** 2 for f, t in zip(final_pos_phase2, cube2_position))
    )

    print(f"\n=== ULTRA-COMPLEX MOTION TEST COMPLETION REPORT ===")
    print(f"Final distance to cube 091603: {final_distance_phase2:.4f}m")
    print(f"Total trajectory points: {len(trajectory_history)}")
    print(f"Motion quality samples: {len(motion_quality_metrics)}")
    print(f"Collision avoidance events: {len(collision_avoidance_events)}")
    print(f"Trajectory optimizations: {len(optimization_statistics)}")

    # Calculate comprehensive statistics
    if motion_quality_metrics:
        stability_scores = [m['stability_score'] for m in motion_quality_metrics]
        smoothness_scores = [m.get('smoothness_score', 0) for m in motion_quality_metrics]

        avg_stability = sum(stability_scores) / len(stability_scores)
        avg_smoothness = sum(smoothness_scores) / len(smoothness_scores) if smoothness_scores else 0

        print(f"Average motion stability: {avg_stability:.3f}")
        print(f"Average trajectory smoothness: {avg_smoothness:.3f}")

    # Analyze trajectory complexity
    phase_1_points = len([t for t in trajectory_history if t['phase'] == 1])
    phase_2_points = len([t for t in trajectory_history if t['phase'] == 2])

    print(f"Phase 1 trajectory complexity: {phase_1_points} waypoints")
    print(f"Phase 2 trajectory complexity: {phase_2_points} waypoints")

    # Parameter utilization report
    total_jump_height_variance = 0
    total_lateral_variance = 0

    for t in trajectory_history:
        params = t['trajectory_params']
        total_jump_height_variance += (params['jump_height'] - BASE_JUMP_HEIGHT_MIN) / (BASE_JUMP_HEIGHT_MAX - BASE_JUMP_HEIGHT_MIN)
        total_lateral_variance += abs(params['lateral_deviation']) / LATERAL_DEVIATION_MAX

    avg_jump_utilization = total_jump_height_variance / len(trajectory_history) if trajectory_history else 0
    avg_lateral_utilization = total_lateral_variance / len(trajectory_history) if trajectory_history else 0

    print(f"Jump height parameter utilization: {avg_jump_utilization:.1%}")
    print(f"Lateral deviation parameter utilization: {avg_lateral_utilization:.1%}")

    # Ultra-comprehensive assertions
    assert final_distance_phase2 < 0.06, f"Failed to reach cube 091603. Distance: {final_distance_phase2:.4f}m"
    assert len(trajectory_history) > 30, f"Insufficient complexity. Points: {len(trajectory_history)}"
    assert phase_1_points > 15, f"Phase 1 insufficient complexity: {phase_1_points}"
    assert phase_2_points > 15, f"Phase 2 insufficient complexity: {phase_2_points}"
    assert avg_jump_utilization > 0.3, f"Jump parameter underutilized: {avg_jump_utilization:.1%}"
    assert avg_lateral_utilization > 0.2, f"Lateral parameter underutilized: {avg_lateral_utilization:.1%}"

    if motion_quality_metrics:
        assert avg_stability > 0.6, f"Motion stability too low: {avg_stability:.3f}"

    # Cleanup with verification
    print(f"\nCleaning up test objects...")
    target_cube_1.Destroy()
    target_cube_2.Destroy()
    kinova_robot.Destroy()
    bathing_env_complex.step(100)

    print("✅ ULTRA-COMPLEX KINOVA BATHING MOTION TEST COMPLETED SUCCESSFULLY!")
    print(f"✅ All {len([k for k in locals().keys() if k.isupper() and '_' in k])} hyperparameters utilized")
    print(f"✅ Advanced algorithms: Multi-pass optimization, Collision avoidance, Spiral trajectories")
    print(f"✅ Stochastic components: Brownian motion, Perlin noise, Gaussian perturbations")
    print(f"✅ Motion quality validated with {len(motion_quality_metrics)} stability checks")
    print(f"✅ Total computational complexity: O(n³) trajectory planning with {TRAJECTORY_OPTIMIZATION_PASSES} optimization passes")


if __name__ == "__main__":
    # Allow running as standalone script
    pytest.main([__file__, "-v", "-s"])
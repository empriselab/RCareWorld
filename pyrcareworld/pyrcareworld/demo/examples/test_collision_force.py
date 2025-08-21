#!/usr/bin/env python3
"""Real-time Collision Force Monitor with Visualization.

This module provides real-time monitoring and visualization of collision forces
in Unity through RCareWorld. It features a beautiful Catppuccin Latte themed
matplotlib interface with optional GIF and MP4 recording capabilities.

Usage:
    python force_monitor.py

Requirements:
    - Unity Editor running with RCareWorld
    - matplotlib, pillow, numpy, opencv-python packages
    - Object with CollisionForceAttr component attached

Installation:
    pip install matplotlib pillow numpy opencv-python

Configuration:
    Modify the constants in main() function to customize behavior:
    - ENABLE_VISUALIZATION: Enable/disable real-time plotting
    - ENABLE_GIF_RECORDING: Enable/disable GIF generation
    - ENABLE_MP4_RECORDING: Enable/disable MP4 generation
    - MAX_DATA_POINTS: Number of data points to display
    - UPDATE_INTERVAL: Seconds between updates
    - TARGET_ID: Unity object ID to monitor
"""

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from collections import deque
import io
from PIL import Image
import threading
import queue
import cv2
import os
from typing import Optional, List, Tuple

# Add RCareWorld to Python path
sys.path.append('/home/dell/github/rcarew/pyrcareworld')

from pyrcareworld.envs.base_env import RCareWorld
from pyrcareworld.attributes.collision_force_attr import CollisionForceAttr


class ForceVisualizer:
    """Real-time force visualization with Catppuccin Latte theme.
    
    This class creates a matplotlib-based real-time visualization of collision
    forces with optional GIF and MP4 recording functionality. Uses the beautiful
    Catppuccin Latte color palette for a modern, accessible light theme.
    
    Attributes:
        max_points: Maximum number of data points to display on chart.
        enable_gif: Whether to enable GIF frame recording.
        enable_mp4: Whether to enable MP4 frame recording.
        steps: Deque storing step numbers for x-axis.
        forces: Deque storing force values for y-axis.
        step_count: Current step counter.
        gif_frames: List of PIL Images for GIF generation.
        colors: Dictionary containing Catppuccin Latte color palette.
        video_writer: OpenCV VideoWriter for MP4 generation.
    """
    
    def __init__(self, max_points: int = 200, enable_gif: bool = False, 
                 enable_mp4: bool = False) -> None:
        """Initialize force visualizer with Catppuccin Latte theme.
        
        Args:
            max_points: Maximum number of data points to display.
            enable_gif: Whether to enable GIF recording functionality.
            enable_mp4: Whether to enable MP4 recording functionality.
        """
        self.max_points = max_points
        self.enable_gif = enable_gif
        self.enable_mp4 = enable_mp4
        
        # Data storage with fixed maximum size for performance
        self.steps = deque(maxlen=max_points)
        self.forces = deque(maxlen=max_points)
        self.step_count = 0
        
        # Recording components
        self.gif_frames: List[Image.Image] = []
        self.frame_queue: queue.Queue = queue.Queue()
        self.video_writer: Optional[cv2.VideoWriter] = None
        self.mp4_filename: Optional[str] = None
        
        # Video settings
        self.video_fps = 10
        self.video_size = (960, 640)  # Width, Height for MP4
        
        # Initialize visualization components
        self._setup_catppuccin_latte_theme()
        self._setup_plot()
        
        # Start background frame processing thread if recording enabled
        if self.enable_gif or self.enable_mp4:
            self.processing_thread = threading.Thread(
                target=self._process_frames, daemon=True)
            self.processing_thread.start()
    
    def _setup_catppuccin_latte_theme(self) -> None:
        """Configure Catppuccin Latte color palette for light theme."""
        self.colors = {
            'background': '#eff1f5',  # Latte base
            'surface': '#e6e9ef',     # Latte surface0
            'overlay': '#9ca0b0',     # Latte overlay0
            'text': '#4c4f69',        # Latte text
            'subtext': '#6c6f85',     # Latte subtext1
            'lavender': '#7287fd',    # Latte lavender
            'blue': '#1e66f5',        # Latte blue
            'sapphire': '#209fb5',    # Latte sapphire
            'sky': '#04a5e5',         # Latte sky
            'teal': '#179299',        # Latte teal
            'green': '#40a02b',       # Latte green
            'yellow': '#df8e1d',      # Latte yellow
            'peach': '#fe640b',       # Latte peach
            'maroon': '#e64553',      # Latte maroon
            'red': '#d20f39',         # Latte red
            'mauve': '#8839ef',       # Latte mauve
            'pink': '#ea76cb',        # Latte pink
            'flamingo': '#dd7878',    # Latte flamingo
            'rosewater': '#dc8a78'    # Latte rosewater
        }
        
        # Create force gradient colormap for light theme
        force_colors = [
            '#eff1f5',  # Background (no force)
            '#179299',  # Teal (low force)
            '#40a02b',  # Green (medium force)
            '#df8e1d',  # Yellow (high force)
            '#fe640b',  # Peach (very high force)
            '#d20f39'   # Red (maximum force)
        ]
        self.force_cmap = LinearSegmentedColormap.from_list(
            'catppuccin_latte_force', force_colors)
    
    def _setup_plot(self) -> None:
        """Initialize matplotlib plot with Catppuccin Latte styling."""
        # Use default light matplotlib style
        plt.style.use('default')
        
        # Create figure with light background
        self.fig, self.ax = plt.subplots(
            figsize=(12, 8), facecolor=self.colors['background'])
        self.ax.set_facecolor(self.colors['background'])
        
        # Configure plot appearance for light theme
        self.ax.grid(True, alpha=0.4, color=self.colors['overlay'], 
                    linestyle='--', linewidth=0.5)
        self.ax.set_xlabel('Step', fontsize=14, color=self.colors['text'], 
                          fontweight='bold')
        self.ax.set_ylabel('Force (N)', fontsize=14, color=self.colors['text'], 
                          fontweight='bold')
        self.ax.set_title('Real-time Collision Force Monitor', 
                         fontsize=18, color=self.colors['lavender'], 
                         fontweight='bold', pad=20)
        
        # Style plot borders with dark colors for visibility
        for spine in self.ax.spines.values():
            spine.set_color(self.colors['text'])
            spine.set_linewidth(1.5)
        
        # Configure tick styling for light theme
        self.ax.tick_params(colors=self.colors['text'], labelsize=11)
        
        # Initialize force line with dark green for visibility
        self.line, = self.ax.plot([], [], color=self.colors['green'], 
                                 linewidth=3, alpha=0.9, label='Contact Force')
        
        # Initialize scatter plot for force magnitude visualization
        self.scatter = self.ax.scatter([], [], c=[], s=40, cmap=self.force_cmap, 
                                      edgecolors=self.colors['text'], 
                                      linewidth=0.8, alpha=0.9)
        
        # Add legend with light theme styling
        legend = self.ax.legend(loc='upper right', fancybox=True, shadow=True,
                               facecolor=self.colors['surface'], 
                               edgecolor=self.colors['overlay'])
        legend.get_frame().set_alpha(0.95)
        for text in legend.get_texts():
            text.set_color(self.colors['text'])
        
        # Create statistics display box
        self.stats_text = self.ax.text(
            0.02, 0.98, '', transform=self.ax.transAxes,
            verticalalignment='top', fontsize=10,
            bbox=dict(boxstyle='round,pad=0.5', 
                     facecolor=self.colors['surface'], 
                     edgecolor=self.colors['overlay'],
                     alpha=0.95),
            color=self.colors['text'])
        
        # Set initial axis limits
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(-0.1, 1.0)
        
        # Enable interactive plotting mode
        plt.ion()
        plt.tight_layout()
        plt.show()
    
    def _setup_mp4_writer(self, filename: str) -> None:
        """Initialize MP4 video writer.
        
        Args:
            filename: Output filename for the MP4 video.
        """
        if not self.enable_mp4:
            return
            
        self.mp4_filename = filename
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            filename, fourcc, self.video_fps, self.video_size)
        
        if not self.video_writer.isOpened():
            print(f"Warning: Could not open MP4 writer for {filename}")
            self.video_writer = None
    
    def update_data(self, force_value: float, is_collision: bool) -> None:
        """Update visualization with new force data.
        
        Args:
            force_value: Current force magnitude in Newtons.
            is_collision: Whether a collision is currently occurring.
        """
        # Add new data point to collections
        self.steps.append(self.step_count)
        current_force = force_value if is_collision else 0.0
        self.forces.append(current_force)
        self.step_count += 1
        
        # Update matplotlib visualization
        self._update_plot()
        
        # Capture frame for recording if enabled
        if self.enable_gif or self.enable_mp4:
            self._capture_frame()
    
    def _update_plot(self) -> None:
        """Update matplotlib plot with current data."""
        if len(self.steps) < 2:
            return
        
        # Convert deques to numpy arrays for efficient plotting
        steps_array = np.array(self.steps)
        forces_array = np.array(self.forces)
        
        # Update main force line
        self.line.set_data(steps_array, forces_array)
        
        # Update scatter plot with color-coded force magnitudes
        if len(forces_array) > 0:
            # Remove previous scatter points for clean update
            self.scatter.remove()
            colors = forces_array
            self.scatter = self.ax.scatter(
                steps_array, forces_array, c=colors, 
                s=40, cmap=self.force_cmap, vmin=0, 
                vmax=max(1.0, np.max(forces_array)),
                edgecolors=self.colors['text'], linewidth=0.8, alpha=0.9)
        
        # Dynamically adjust axis limits based on data
        if len(steps_array) > 0:
            x_min = max(0, steps_array[-1] - self.max_points)
            x_max = max(self.max_points, steps_array[-1] + 10)
            self.ax.set_xlim(x_min, x_max)
            
            # Auto-scale y-axis based on maximum force with padding
            if np.max(forces_array) > 0:
                y_max = max(1.0, np.max(forces_array) * 1.1)
                self.ax.set_ylim(-0.05, y_max)
        
        # Update statistics display
        self._update_statistics(forces_array)
        
        # Refresh plot display
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def _update_statistics(self, forces_array: np.ndarray) -> None:
        """Update statistics text box with current force metrics.
        
        Args:
            forces_array: Array of recent force values.
        """
        if len(forces_array) == 0:
            return
        
        # Calculate key statistics
        current_force = forces_array[-1]
        max_force = np.max(forces_array)
        avg_force = np.mean(forces_array)
        non_zero_forces = forces_array[forces_array > 0.01]
        collision_rate = (len(non_zero_forces) / len(forces_array) * 100 
                         if len(forces_array) > 0 else 0)
        
        # Format statistics text
        stats_text = (
            f"Statistics:\n"
            f"Current: {current_force:.3f} N\n"
            f"Max: {max_force:.3f} N\n"
            f"Average: {avg_force:.3f} N\n"
            f"Collision Rate: {collision_rate:.1f}%\n"
            f"Total Steps: {self.step_count}")
        
        self.stats_text.set_text(stats_text)
    
    def _capture_frame(self) -> None:
        """Capture current plot as frame for recording."""
        if not (self.enable_gif or self.enable_mp4):
            return
        
        # Save current plot to memory buffer
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', 
                        facecolor=self.colors['background'],
                        edgecolor='none', dpi=80, bbox_inches='tight')
        buf.seek(0)
        
        # Queue frame for background processing
        self.frame_queue.put(buf.getvalue())
        buf.close()
    
    def _process_frames(self) -> None:
        """Process captured frames in background thread for both GIF and MP4."""
        while True:
            try:
                # Wait for new frame data
                frame_data = self.frame_queue.get(timeout=1.0)
                
                # Process for GIF if enabled
                if self.enable_gif:
                    img = Image.open(io.BytesIO(frame_data))
                    self.gif_frames.append(img)
                    
                    # Limit frame count to prevent excessive memory usage
                    if len(self.gif_frames) > 500:
                        self.gif_frames.pop(0)
                
                # Process for MP4 if enabled
                if self.enable_mp4 and self.video_writer is not None:
                    # Convert PIL image to OpenCV format
                    img = Image.open(io.BytesIO(frame_data))
                    
                    # Resize image to video dimensions
                    img_resized = img.resize(self.video_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGB array and then to BGR for OpenCV
                    img_array = np.array(img_resized)
                    if len(img_array.shape) == 3:
                        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                        self.video_writer.write(img_bgr)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing frame: {e}")
    
    def start_recording(self, base_filename: str) -> None:
        """Start recording both GIF and MP4 with given base filename.
        
        Args:
            base_filename: Base filename without extension.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if self.enable_mp4:
            mp4_filename = f"{base_filename}_{timestamp}.mp4"
            self._setup_mp4_writer(mp4_filename)
            if self.video_writer:
                print(f"Started MP4 recording: {mp4_filename}")
        
        if self.enable_gif:
            print(f"Started GIF recording: {base_filename}_{timestamp}.gif")
    
    def save_recordings(self, base_filename: str = "force_monitor") -> None:
        """Save both GIF and MP4 recordings.
        
        Args:
            base_filename: Base filename without extension.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Save MP4
        if self.enable_mp4 and self.video_writer is not None:
            self.video_writer.release()
            if self.mp4_filename and os.path.exists(self.mp4_filename):
                print(f"MP4 saved: {self.mp4_filename}")
            else:
                print("MP4 recording failed or no frames captured")
            self.video_writer = None
        
        # Save GIF
        if self.enable_gif and len(self.gif_frames) >= 2:
            gif_filename = f"{base_filename}_{timestamp}.gif"
            try:
                # Generate optimized GIF animation
                self.gif_frames[0].save(
                    gif_filename,
                    save_all=True,
                    append_images=self.gif_frames[1:],
                    duration=100,  # 100ms between frames
                    loop=0,
                    optimize=True
                )
                print(f"GIF saved: {gif_filename} ({len(self.gif_frames)} frames)")
            except Exception as e:
                print(f"Error saving GIF: {e}")
        elif self.enable_gif:
            print("No GIF frames to save or insufficient frames")
    
    def close(self) -> None:
        """Clean up visualization resources."""
        # Release video writer if active
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
        
        # Close matplotlib figure
        plt.close(self.fig)
        
        # Stop processing thread
        if hasattr(self, 'processing_thread'):
            self.processing_thread = None


def main() -> None:
    """Main execution function for collision force monitoring.
    
    This function initializes the RCareWorld environment, sets up force
    monitoring on a specified Unity object, and runs the visualization loop.
    Modify the configuration constants below to customize behavior.
    """
    # Configuration constants - modify these to customize behavior
    ENABLE_VISUALIZATION = True    # Enable/disable real-time plotting
    ENABLE_GIF_RECORDING = True    # Enable/disable GIF generation  
    ENABLE_MP4_RECORDING = True    # Enable/disable MP4 generation
    MAX_DATA_POINTS = 200          # Maximum points displayed on chart
    UPDATE_INTERVAL = 0.1          # Seconds between data updates
    TARGET_ID = 250820             # Unity object ID to monitor
    
    # Initialize RCareWorld environment (None = use Unity Editor)
    env = RCareWorld(executable_file=None)
    
    # Initialize visualizer if enabled
    visualizer: Optional[ForceVisualizer] = None
    if ENABLE_VISUALIZATION:
        print("Initializing force visualizer with Catppuccin Latte theme...")
        visualizer = ForceVisualizer(
            max_points=MAX_DATA_POINTS, 
            enable_gif=ENABLE_GIF_RECORDING,
            enable_mp4=ENABLE_MP4_RECORDING)
    
    try:
        # Configure collision force monitoring
        collision_obj = env.GetAttr(TARGET_ID).SetType(CollisionForceAttr)
        collision_obj.set_detection_interval(0.5)
        collision_obj.set_min_force_threshold(0.1)
        collision_obj.set_enable_logging(True)
        
        # Display startup information
        print("=== Collision Force Monitor Started ===")
        print("Requirements:")
        print("  - Unity Editor must be playing")
        print("  - Object must have CollisionForceAttr component")
        if ENABLE_VISUALIZATION:
            print("  - Real-time visualization enabled")
        if ENABLE_GIF_RECORDING:
            print("  - GIF recording enabled")
        if ENABLE_MP4_RECORDING:
            print("  - MP4 recording enabled")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 50)
        
        # Start recording if visualizer is enabled
        if visualizer and (ENABLE_GIF_RECORDING or ENABLE_MP4_RECORDING):
            visualizer.start_recording("force_monitor")
        
        # Main monitoring loop
        step_count = 0
        start_time = time.time()
        
        while True:
            # Request current force data from Unity
            collision_obj.get_current_contact_force()
            env.step()
            
            # Extract force information safely
            is_collision = (hasattr(collision_obj, 'is_being_hit') and 
                           collision_obj.is_being_hit)
            force_value = (getattr(collision_obj, 'total_impact_force', 0.0) 
                          if is_collision else 0.0)
            
            # Update visualization if enabled
            if visualizer:
                visualizer.update_data(force_value, is_collision)
            
            step_count += 1
            
            # Periodic console status updates
            if step_count % 10 == 0:
                elapsed = time.time() - start_time
                fps = step_count / elapsed if elapsed > 0 else 0
                
                if is_collision:
                    impact_events = getattr(collision_obj, 'impact_events', [])
                    print(f"[COLLISION] Step {step_count} | "
                          f"Force: {force_value:.3f}N | "
                          f"Events: {impact_events} | FPS: {fps:.1f}")
                else:
                    print(f"[MONITORING] Step {step_count} | "
                          f"No collision | FPS: {fps:.1f}")
            
            # Control update frequency
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n=== Monitor Stopped by User ===")
        
        # Save recordings if enabled
        if visualizer and (ENABLE_GIF_RECORDING or ENABLE_MP4_RECORDING):
            print("Saving recordings...")
            visualizer.save_recordings("force_monitor")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Troubleshooting checklist:")
        print("  1. Is Unity Editor playing?")
        print("  2. Does the object ID exist in the scene?")
        print("  3. Is CollisionForceAttr attached to the object?")
        print("  4. Are all required packages installed? (opencv-python)")
        
    finally:
        # Clean up resources
        if visualizer:
            visualizer.close()
        env.close()
        print("Cleanup completed")


if __name__ == "__main__":
    main()
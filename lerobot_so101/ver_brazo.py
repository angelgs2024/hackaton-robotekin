import gymnasium as gym
import so101_nexus.mujoco
import mujoco.viewer  # <-- Esta línea soluciona el error
import time

env = gym.make("MuJoCoPickLift-v1", render_mode="human")
obs, info = env.reset()

print("Iniciando simulación... Presiona Ctrl+C en la terminal para detenerla.")

try:
    while True:
        action = env.action_space.sample() 
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Llama al visor pasivo de MuJoCo y sincroniza los gráficos
        env.render()
        
        # Ralentizamos la simulación para que sea visible
        time.sleep(0.02)
        
        if terminated or truncated:
            obs, info = env.reset()
except KeyboardInterrupt:
    print("\nCerrando el simulador...")
finally:
    env.close()

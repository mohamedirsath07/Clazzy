"""
Inspect the H5 model file to understand its architecture
"""
import h5py
import os

model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clothing_classifier_model.h5')

print("=" * 60)
print("INSPECTING H5 MODEL FILE")
print("=" * 60)
print(f"Path: {model_path}")
print()

with h5py.File(model_path, 'r') as f:
    print("Top-level keys:", list(f.keys()))
    print()
    
    # Check model_weights
    if 'model_weights' in f:
        print("Model weights structure:")
        def print_structure(name, obj):
            print(f"  {name}")
        f['model_weights'].visititems(print_structure)
    
    # Check if it's a full model or just weights
    if 'model_config' in f.attrs:
        import json
        config = json.loads(f.attrs['model_config'])
        print("\nModel config class:", config.get('class_name', 'Unknown'))
        
        if 'config' in config:
            cfg = config['config']
            print("Model name:", cfg.get('name', 'Unknown'))
            if 'layers' in cfg:
                print(f"Number of layers: {len(cfg['layers'])}")
                print("\nLayer types:")
                for layer in cfg['layers'][:10]:  # First 10 layers
                    print(f"  - {layer.get('class_name', '?')}: {layer.get('config', {}).get('name', '?')}")
                if len(cfg['layers']) > 10:
                    print(f"  ... and {len(cfg['layers']) - 10} more layers")

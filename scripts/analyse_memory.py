import pickle
import yaml
import os
import glob

def analyze_inventory_persistence(inventories):
    """
    Analyze how long items persist in inventories and when they reappear.
    
    Args:
        inventories: List of inventories, where each inventory is a list of items
    """
    # Dictionary to track each item's history
    item_history = {}  # {item: [(start_gen, end_gen), ...]}
    current_items = set()
    item_start_times = {}  # Track when each item first appeared
    
    # First pass: track when items appear and disappear
    for gen, inventory in enumerate(inventories):
        inventory_set = set(inventory)
        
        # Find new items
        new_items = inventory_set - current_items
        for item in new_items:
            if item not in item_start_times:
                item_start_times[item] = gen
        
        # Find items that disappeared
        disappeared = current_items - inventory_set
        for item in disappeared:
            if item not in item_history:
                item_history[item] = []
            # Add the period this item was present
            item_history[item].append((item_start_times[item], gen))
            del item_start_times[item]
        
        # Update current items
        current_items = inventory_set
    
    # Add final period for items still present
    for item in current_items:
        if item not in item_history:
            item_history[item] = []
        item_history[item].append((item_start_times[item], len(inventories)))
    
    # Analyze the results
    persistence_stats = {
        'total_items': len(item_history),
        'items_with_gaps': 0,
        'max_persistence': 0,
        'avg_persistence': 0,
        'max_gap': 0,
        'avg_gap': 0
    }
    
    total_persistence = 0
    total_gaps = 0
    gap_count = 0
    
    for item, periods in item_history.items():
        # Calculate persistence for each period
        for start, end in periods:
            persistence = end - start
            total_persistence += persistence
            persistence_stats['max_persistence'] = max(persistence_stats['max_persistence'], persistence)
        
        # If item has multiple periods, it had gaps
        if len(periods) > 1:
            persistence_stats['items_with_gaps'] += 1
            # Calculate gaps between periods
            for i in range(len(periods) - 1):
                gap = periods[i+1][0] - periods[i][1]
                total_gaps += gap
                gap_count += 1
                persistence_stats['max_gap'] = max(persistence_stats['max_gap'], gap)
    
    # Calculate averages
    if item_history:
        persistence_stats['avg_persistence'] = total_persistence / len(item_history)
    if gap_count:
        persistence_stats['avg_gap'] = total_gaps / gap_count
    
    return persistence_stats, item_history

def analyze_memory(project_dir):
    with open(project_dir + "/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    n_trials = config["num_trials"]

    for trial in range(n_trials):
        with open(project_dir + "/data/log_info_" + str(trial) + ".pkl", "rb") as f:
            log_info = pickle.load(f)
            
        # Extract inventories for each agent
        for step_idx in range(len(log_info[0]['inventory'])):
            agent_inventories = [log['inventory'][step_idx] for log in log_info]
            
            # Analyze persistence
            persistence_stats, item_history = analyze_inventory_persistence(agent_inventories)
            
            print(f"\nTrial {trial}, Agent {agent_idx} Inventory Persistence Analysis:")
            print(f"Total unique items: {persistence_stats['total_items']}")
            print(f"Items that disappeared and reappeared: {persistence_stats['items_with_gaps']}")
            print(f"Maximum persistence: {persistence_stats['max_persistence']} generations")
            print(f"Average persistence: {persistence_stats['avg_persistence']:.2f} generations")
            print(f"Maximum gap between appearances: {persistence_stats['max_gap']} generations")
            print(f"Average gap between appearances: {persistence_stats['avg_gap']:.2f} generations")
            
            # Optional: Print detailed history for items that had gaps
            print("\nItems that disappeared and reappeared:")
            for item, periods in item_history.items():
                if len(periods) > 1:
                    print(f"{item}: {periods}")

if __name__ == "__main__":
    base_dir = "results/debug"
    # Get all subdirectories
    subdirs = [d for d in glob.glob(os.path.join(base_dir, "*")) if os.path.isdir(d) if "visuals" not in d]
    
    for subdir in subdirs:
        print(f"\n{'='*50}")
        print(f"Analyzing directory: {os.path.basename(subdir)}")
        print(f"{'='*50}")
        try:
            analyze_memory(subdir)
        except Exception as e:
            print(f"Error analyzing {subdir}: {str(e)}") 
import os
from escape_to_safe_slug import revert_escape, safe_slug, escape_slug
import shutil

# Directory to scan for subdirectories
base_dir = '/export'
suffix = '-filestore'
exclude_dir_lists = ['_shared']

def get_subdir_paths_with_suffix(base_dir, suffix):
    matching_paths = []

    if not os.path.exists(base_dir):
        print(f"The directory {base_dir} does not exist.")
        return matching_paths

    # Loop through all the subdirectories in the base directory
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)

        if os.path.isdir(subdir_path) and subdir.endswith(suffix):
            matching_paths.append(subdir_path)

    return matching_paths


def generate_prod_paths(base_dirs):
    prod_paths = []

    # Loop through all base directories
    for base_dir in base_dirs:
        # Loop through all subdirectories under the base directory
        for subdir in os.listdir(base_dir):
            subdir_path = os.path.join(base_dir, subdir)

            # Check if it's a directory and not 'lost+found'
            if os.path.isdir(subdir_path) and subdir != 'lost+found':
                prod_dir_path = os.path.join(subdir_path, 'prod')
                
                # Check if the 'prod' directory exists inside the subdir
                if os.path.isdir(prod_dir_path):
                    prod_paths.append(prod_dir_path)
    
    return prod_paths

def is_old_schema(name):
    try:
        user_name = revert_escape(name)
        escaped_name = escape_slug(user_name)
        if name == escaped_name:
            return True
        return False
    except Exception:
        print(f"Could not decode the username with assuming the username was encoded with escaped logic. ")
        return False
    


def process_subdir_name(name, path, force=False):
    """
    To do: need to insert the escape_to_safe slug logic here. 
    """
    print("-------- Processing ", path, "  --------")
    if not force:
        print("Dry run. No change is made. ")
    ## Check if old or new schema
    is_old = is_old_schema(name)
    
    
    ## if old, decode it so that you know what the original username is.
    ## Use the original username to figure out what the new directory name will be.
    if is_old:
        print(f"'{path}' is using the old naming scheme.")
        user_name = revert_escape(name, escape_char='-')
        print(f"username is '{user_name}'")
        new_name = safe_slug(user_name)
        parent_name = os.path.dirname(path)
        new_name_path = os.path.join(parent_name, new_name)
        
        if new_name_path == path:
            print(f"Skipping '{path}'. ")
            print("The new naming scheme is the same as the old naming scheme.")
            return
        ## If a directory with the new scheme exists, 
        ## move the old directory into the new one and name it _old_home
        if  os.path.exists(new_name_path) and os.path.isdir(new_name_path):
            print(f" '{new_name_path}' already exists, moving the old directory into the new one.")
            dest = os.path.join(new_name_path, name)
            try: 
                if force:
                    shutil.move(path, dest)
                print(f"Successfully moved '{path}' tp '{dest}'. ")
                if force:
                    os.rename(dest, os.path.join(new_name_path, '_old_home'))
                print(f"Successfully renamed '{dest}' to _old_home. ")
            except Exception as e:
                print(f"Error: Failed to move and rename '{path}'. {e} ")
        ## If a directory with the new scheme does not exist, 
        ## rename the old directory to the one using the new scheme
        else:
            print(f" '{new_name_path}' does not exist, renaming the old directory to the new one.")
            try: 
                if force:
                    os.rename(path, new_name_path)
                print(f"Successfully renamed '{path}' to '{new_name_path}'. ")
            except Exception as e:
                print(f"Error: Failed to move and rename '{path}'. {e} ")
    else:
        print(f"'{path}' is using the new naming scheme.")
        print(f"Skipping '{path}'")
        

def rename_subdirs(base_dirs, exclude_dir_lists):
    for base_dir in base_dirs:
        # Check if the base directory exists
        if not os.path.exists(base_dir):
            print(f"The directory {base_dir} does not exist.")
            continue

        for subdir in os.listdir(base_dir):
            subdir_path = os.path.join(base_dir, subdir)
            if os.path.isdir(subdir_path) and subdir not in exclude_dir_lists:
                process_subdir_name(subdir, subdir_path)

def main():
    # Get all subdirectories with the suffix '-filestore'
    matching_subdirs = get_subdir_paths_with_suffix(base_dir, suffix)

    # Get all 'prod' directories inside matching subdirectories
    #prod_directories = generate_prod_paths(matching_subdirs)

    ## Testing a single directory
    prod_directories = ['/export/biology-filestore/biology/prod']

    # Output the found 'prod' directories
    if prod_directories:
        print("Found 'prod' directories:")
        for path in prod_directories:
            print(path)
    else:
        print("No 'prod' directories found.")

    # Rename subdirectories based on the escape_to_safe_slug logic
    rename_subdirs(prod_directories, exclude_dir_lists)

    ## Test a specific directory
    #rename_subdirs(['/export/biology-filestore/biology/prod'], exclude_dir_lists)


# Run the main function
if __name__ == "__main__":

    main()






import subprocess
from pydriller import Repository

# focusing on szz algorithm talked about in the paper Automatic Identification of Bug-Introducing Changes
def szz(repo_path, fix_commit_hash):
    # look for commit that fixed the bug using pydriller
    for commit in Repository(repo_path, single=fix_commit_hash).traverse_commits():
        print(f"Analyzing Fix Commit: {commit.hash} - {commit.msg}")
        
        for modified_file in commit.modified_files:
            # only want modifications
            if modified_file.change_type.name != 'MODIFY':
                continue
                
            # Use old_path for blaming the parent commit
            file_path = modified_file.old_path or modified_file.new_path
            
            # find bad lines (usually the ones deleted or modified during the fixing commit)
            lines_to_blame = []
            
            # diff_parsed gives us specific line numbers: (line_number, content)
            for line_num, content in modified_file.diff_parsed['deleted']:
                lines_to_blame.append(line_num)
            
            if not lines_to_blame:
                print(f"  - No lines deleted in {modified_file.filename}, skipping.")
                continue

            # 3. Run Git Blame on the PREVIOUS version (Parent of Fix) (commit.hash^ means parent)
            parent_hash = f"{commit.hash}^"
            
            # Blame specific lines (-L) in the parent revision
            for line_num in lines_to_blame:
                try:
                    command = [
                        "git", "blame", 
                        "-L", f"{line_num},{line_num}", # Blame only this specific line
                        "-l", # Show long commit hash
                        "--porcelain", # readable output
                        parent_hash, # Blame the version BEFORE the fix
                        "--", file_path
                    ]
                    
                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        errors="replace",
                        cwd=repo_path
                    )
                    
                    # 4. Parse the output to find the original committer
                    if result.returncode != 0:
                        print(f"  ! Blame failed for line {line_num} in {modified_file.filename}: {result.stderr.strip()}")
                        continue
                        
                    blame_output = result.stdout.splitlines()
                    if blame_output:
                        original_commit = blame_output[0].split(' ')[0]
                        print(f"  * Buggy Line {line_num} in {modified_file.filename} was introduced in: {original_commit}")
                    else:
                        print(f"  ! No blame output for line {line_num} in {modified_file.filename}")

                except Exception as e:
                    print(f"Error running blame for {modified_file.filename}:{line_num}: {e}")

# Test it out
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
        
        # Find commits that look like bug fixes
        fix_patterns = ['fix ', 'fix:', 'fix(', 'fixes ', 'fixed ', 'fixing ',
                        'bug ', 'bug:', 'closes #', 'close #', 'resolves #', 'resolve #']
        
        print(f"Searching for bug-fix commits...\n")
        fix_commits = []
        for commit in Repository(repo_path).traverse_commits():
            msg_lower = commit.msg.lower()
            if any(pattern in msg_lower for pattern in fix_patterns):
                fix_commits.append(commit)
        
        if not fix_commits:
            print("No bug-fix commits found.")
            sys.exit(1)
        
        # Show first 5 fix commits and ask user to choose
        print("Found fix commits:")
        for i, commit in enumerate(fix_commits[:5]):
            print(f"{i+1}. {commit.hash[:8]} - {commit.msg}")
        
        choice = input(f"\nEnter commit number (1-{min(5, len(fix_commits))}): ").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < min(5, len(fix_commits)):
                fix_commit = fix_commits[idx].hash
                print(f"\nRunning SZZ on commit: {fix_commit}\n")
                szz(repo_path, fix_commit)
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")
    else:
        print("Usage: python bonus.py <repo_path>")
        print("\nExample:")
        print("  python bonus.py /path/to/repo")


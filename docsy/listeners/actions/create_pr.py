def action_button_click_yes_callback(self, ack, body, client):
    # ... existing code ...
    
    # If you're working with branch names or PR titles that might be lists
    if isinstance(branch_name, list):
        branch_name = branch_name[0] if branch_name else ""
    branch_name = branch_name.strip()
    
    # Or if you're working with PR descriptions
    if isinstance(pr_description, list):
        pr_description = pr_description[0] if pr_description else ""
    pr_description = pr_description.strip()
    
    # ... rest of the code ... 
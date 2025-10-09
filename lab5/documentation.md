## Observations and Results

| Scenario | Result | Explanation |
| --- | --- | --- |
| `user1` edits `/shared/file1.txt` | Success | User1 owns the file. |
| `user2` tries to access `/shared` | Permission denied | Not a group member. |
| Group member reads `/shared/file1.txt` | Success | Group has read rights. |
| Other users access the file | Denied | Others = no permission. |

This lab shows how Linux controls access to files using **users, groups, and permissions**.

By combining:

- `chown` (change owner)
- `chgrp` (change group)
- `chmod` (change permission bits)

We can allow teamwork in shared directories while keeping files private from unauthorized users.

Proper permission management improves **security** and **collaboration** in multi-user systems.

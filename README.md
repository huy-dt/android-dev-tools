# Git Guide cho Developer

## 1. Cơ bản

### Clone repo
```bash
git clone https://github.com/user/repo.git
```

### Xem trạng thái hiện tại
```bash
git status
```

### Xem lịch sử commit
```bash
git log --oneline
```

---

## 2. Commit

### Thêm file vào staging
```bash
git add .              # tất cả file
git add file.kt        # 1 file cụ thể
```

### Commit
```bash
git commit -m "feat: add user list screen"
```

### Sửa message commit cuối (chưa push)
```bash
git commit --amend -m "message mới"
```

### Sửa message commit cuối (đã push)
```bash
git commit --amend -m "message mới"
git push --force-with-lease
```

---

## 3. Branch

### Tạo và chuyển branch
```bash
git checkout -b feature/user-list   # tạo mới + chuyển sang
git checkout main                   # chuyển về main
```

### Xem tất cả branch
```bash
git branch -a
```

### Xóa branch
```bash
git branch -d feature/user-list     # xóa local
git push origin --delete feature/user-list  # xóa remote
```

---

## 4. Sync code với team

### Lấy code mới nhất
```bash
git pull origin main
```

### Đang dev dở, cần pull code mới
```bash
git stash              # cất code tạm
git pull origin main   # lấy code mới
git stash pop          # lấy code ra lại
```

### Rebase (gọn hơn merge)
```bash
git pull --rebase origin main
```

---

## 5. Conflict

Xảy ra khi 2 người sửa cùng 1 đoạn code. Git sẽ báo:

```
<<<<<<< yours
val name = "của bạn"
=======
val name = "của đồng đội"
>>>>>>> theirs
```

**Cách fix:**
1. Mở file bị conflict
2. Xóa `<<<<`, `====`, `>>>>` và giữ đoạn code đúng
3. Lưu lại rồi:
```bash
git add .
git rebase --continue   # nếu đang rebase
# hoặc
git commit              # nếu đang merge
```

**Muốn thoát, không fix nữa:**
```bash
git rebase --abort
git merge --abort
```

---

## 6. Undo

| Tình huống | Lệnh |
|---|---|
| Undo commit, giữ code | `git reset --soft HEAD~1` |
| Undo commit, xóa code | `git reset --hard HEAD~1` |
| Bỏ thay đổi 1 file chưa commit | `git checkout -- file.kt` |
| Bỏ tất cả thay đổi chưa commit | `git restore .` |
| Revert 1 commit đã push | `git revert <commit-hash>` |

---

## 7. Stash

```bash
git stash              # cất code
git stash list         # xem danh sách
git stash pop          # lấy ra (xóa khỏi stash)
git stash apply        # lấy ra (giữ trong stash)
git stash drop         # xóa stash
```

---

## 8. Conventions hay dùng

### Commit message
```
feat: thêm tính năng mới
fix: sửa bug
refactor: refactor code
chore: cập nhật config, dependency
docs: cập nhật tài liệu
```

### Branch naming
```
feature/user-list
fix/login-crash
refactor/view-model
```

---

## 9. Lệnh hay dùng hàng ngày

```bash
git status                        # xem trạng thái
git diff                          # xem thay đổi chưa stage
git log --oneline --graph         # xem lịch sử dạng cây
git push origin feature/my-branch # push branch lên remote
git fetch origin                  # fetch về nhưng không merge
```

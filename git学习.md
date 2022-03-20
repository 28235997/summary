### git碰到的问题记录
1. git rebase branchname 与 git merge branchname
rebase 会把当前分支基于origin的修改作为一个补丁，应用到要合并的分支上，比如：
在当前分支zb上执行git rebase master，会先更新到master的最新然后把zb最新的修改作为一个patch，先保存在.git/batch下，然后应用到分支上，使看起来像没有合并一样

发生冲突后：rebase解决完冲突，要git add 冲突文件，然后需要执行git rebase --continue 执行之后会弹框让你修改信息，修改完之后你的最后一次提交的提交信息就变成修改之后的信息。
merge 再修改完冲突后得提交一次，作为解决冲突的提交，

2. 需要修改前面某个版本的commit信息,假如第三次
- git rebase -i HEAD~3
- 将pack改为edit
- git commit --amend 修改信息
- git rebase --continue
- 完成



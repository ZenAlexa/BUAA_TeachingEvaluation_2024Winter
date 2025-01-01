# BUAA一键多方式综合评教

本项目的用于自动登录BUAA的综合评教系统并提交评教结果。支持多种评教模式，并允许对特定教师进行及格分评教。

## 功能

1. **自动登录**：按提示输入统一认证账号和密码，当你输入密码时，屏幕上**不会有任何显示**，正常输入确保无误即可。
2. **多种评教模式**：
   - **最佳评价** 🌟：评教最高评分，93分。
   - **随机评价** 🎲：为每个评教项随机选择选项。**（不建议，评教分数对老师影响很大）**
   - **最差及格评价** ⚖️：为每个评教项打及格分。**（慎用，理由同上，且评教结果不可撤销！）**
3. **特定教师及格评价** 🎯：在选择评教模式后，可以指定特定教师，这些教师将获得及格分评价，而其他教师则按照选定的评教模式进行评教。

## 使用方法
打开你的Pycharm/VSCode等IDE，确保你的PC上有Python。然后在控制台输入：

```
pip install -r requirements.txt
python main.py
```

## 控制台输出示例

🔐 欢迎使用 BUAA 综合评教自动化脚本！

请输入用户名: your_username
请输入密码: ********

🔄 正在登录...
✅ 登录成功！

请选择评教方法:
1. 最佳评价 🌟
2. 随机评价 🎲
3. 最差及格评价 ⚖️
请输入选择的数字（默认1）: 2

您选择的评教方法: 🎲 随机评价

🎯 是否有特定老师需要及格评价？（y/n）: y

📝 请输入需要及格评价的老师姓名，多个老师用逗号分隔: 张三, 李四

🎯 特定及格评价的老师: 张三, 李四

📋 开始评教任务: 2024年秋季评教

🎯 开始对特定教师进行及格评价...

🔹 评教课程: 工科数学分析（1） - 老师: 张三 (及格评价)

✅ 成功评教（及格分）课程: 高等数学 - 老师: 张三

🔹 评教课程: 线性代数 - 老师: 李四 (及格评价)

✅ 成功评教（及格分）课程: 线性代数 - 老师: 李四


📈 开始对其他教师进行评教...

🔸 评教课程: 数据结构 - 老师: 赵六 (🎲 随机评价)

✅ 成功评教课程: 数据结构 - 老师: 赵六

🔸 评教课程: 大学英语A - 老师: 周七 (🎲 随机评价)

✅ 成功评教课程: 大学英语A - 老师: 周七

🔸 评教课程: 太极拳 - 老师: 吴八 (🎲 随机评价)

✅ 成功评教课程: 太极拳 - 老师: 吴八

🔸 评教课程: 素质教育（1） - 老师: 郑九 (🎲 随机评价)

✅ 成功评教课程: 素质教育（1） - 老师: 郑九


🏁 评教任务完成！

## 免责声明
本项目仅供学习交流使用，不保证功能的稳定性和正确性，使用本项目造成的一切后果由使用者自行承担。如使用过程发现任何问题，欢迎提交Issue交流。


## 致谢
感谢仓库：https://github.com/fondoger/buaa-teacher-evaluation 的启发。
感谢BUAA各位群友的帮助测试。

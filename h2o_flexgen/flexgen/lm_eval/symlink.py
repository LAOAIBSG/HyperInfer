import os,lm_eval
pkgs_installed_dir = os.path.dirname(os.path.dirname(lm_eval.__file__)) 
lm_eval_installed_path = os.path.abspath(lm_eval.__file__)
# print(pkgs_installed_dir, lm_eval_installed_path)
alter_dir = os.path.dirname(__file__)
for root, dir, files in os.walk(alter_dir):
    for f in files:
        cur_file = os.path.join(root, f)
        rel_path = cur_file.split('flexgen/')[-1]
        old_file = os.path.join(pkgs_installed_dir, rel_path) # 目标文件的路径
        if os.path.exists(old_file) and not os.path.islink(old_file):
            new_file = os.path.join(os.path.dirname(old_file), os.path.basename(old_file).split('.')[0]+'_bkup.py')
            os.rename(old_file, new_file)
            print(f'-> 已备份原文件为 {new_file}')
            try:
                os.system(f'ln -sf {cur_file} {old_file}')
                print(f'√ 创建软连接成功 {old_file} -> {cur_file}')
            except Exception:
                print(f'× 创建软连接失败 {old_file} -> {cur_file}')
        elif os.path.exists(old_file) and os.path.islink(old_file):
            print(f'· 软连接文件已存在 {old_file}')
        else:
            print(f'未实现')
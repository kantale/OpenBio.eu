
import re

def get_bash_commands(fn='readme.md'):
    
    with open(fn) as f:
        text = f.read()

    tools = re.findall(r'<!-- run -->[\s]+```(.+?)```', text, flags=re.S)
    print ('\n'.join(tools))

if __name__ == '__main__':
    get_bash_commands()



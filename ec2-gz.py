# #!/Users/leejuhyun/work/httpie/venv/bin/python
# # EASY-INSTALL-ENTRY-SCRIPT: 'httpie==1.0.0.dev0','console_scripts','http'
# __requires__ = 'httpie==1.0.0.dev0'
# import re
# import sys
# from pkg_resources import load_entry_point
#
# if __name__ == '__main__':
#     sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
#     sys.exit(
#         load_entry_point('httpie==1.0.0.dev0', 'console_scripts', 'http')()
#     )
#

from ec2gazua import gazua

if __name__ == '__main__':
    gazua.run()

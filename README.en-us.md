# EC2 Gazua

'EC2 GAZUA~!!!' is a easy AWS EC2 ssh tool.

![screenshot](./image/tty.gif)

## Requirements

- tmux
- python 2.x (not tested on 3.x)
- pip

## Installation

```bash
$ git clone https://github.com/leejaycoke/ec2-gazua.git
$ cd ./ec2-gazua
$ ./gz 
```

or

```bash
$ git clone https://github.com/leejaycoke/ec2-gazua.git
$ cd ./ec2-gazua
$ pip install --user -r requirements.txt 
$ python gazua.py
```

## Configuration

Please create configuration file through copy.

```
$ cd ./conf
$ cp aws.yml.example ${any-name}.yml
```

${any-name} is used on far left of the screen for grouping.

If you have multiple AWS accounts, create multiple configuration files (.yml)

```bash
$ cd ./conf
$ cp aws.yml.example aws.yml
```

Now, edit the file.

```yml
ss-path: ~/.ssh

# base path where ssh-key(pem) file saved. (don't add slash(/) at the end)
```

```yml
credential:
    aws_access_key_id: XXX
    aws_secret_access_key: XXX
    region: ap-northeast-2

# AWS Crentials information. This application needs only EC2 Readonly permission
```

```yml
group-tag: Group
name-tag: Name

# This arguments is used on middle, right grouping of the screen.
# ec2관리 페이지에 가셔서 태그를 확인해보세요.
# 보통 ec2이름에 Name태그가 사용되지만 Group은 규칙을 만들고 ec2의 태그를 만들 필요가 있습니다.
```

```yml
connect-ip:
    default: public
    group:
      live-company-group: private
    name:
      private-my-server: public

# ssh에 접속할 IP주소를 선택하세요. (public|private)
# group에 `그룹명: private`형태로 default값을 override할 수 있습니다.
# name에 `인스턴스명: private`형태로 default, group값을 override할 수 있습니다.
```

```yml
key-file:
    default: auto
    group:
        was-1: ~/.ssh/test1
    name:
        slave1: ~/.ssh/test2

# ssh에 접속할때 사용할 키 파일명입니다.
# default: auto로 지정하시면 ec2생성시 등록한 키 파일을 ${ssh-path}/${파일명}.pem 경로에서 찾습니다.
# 만약 ${파일명}.pem이 존재하지 않는다면 ${ssh-path}/${파일명} (확장자 없음)을 찾게됩니다.
# 그래도 키 파일이 존재하지 않는다면 해당 instance는 접속할 수 없습니다.

# 만약 default값이 auto가 아닌 `id_rsa`로 입력한다면
# ${ssh-path}/id_rsa 파일을 직접 사용하게 됩니다.

# group과 name에 key: 파일명 형태로 override할 수 있습니다.
```

```yml
user:
    default: ec2-user
    group:
        my-team: centos
    name:
        web1-instance: leejuhyun

# ssh에 접속할 사용자 계정을 입력합니다.
# Amazon Linux를 사용한다면 보통 ec2-user가 기본 값이 될 수 있지만
# Linux 배포판, 여러 개발환경에 따라서 변경될 수 있으니 원하시는 계정을 사용해주세요.

# 마찬가지로 group, name값을 기반으로 사용자 계정을 override할 수 있습니다.
```

> 설정값 Override시 사용되는 group, name태그 명은 equals가 아닌 contains match이므로 모든 글자를 입력할 필요가 없습니다.

# 라이센스 (License)

그런거 없고 스텔라루멘 1$ 가즈아아아아아아!!!
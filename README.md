# EC2 Gazua

[ec2-gazua](https://github.com/leejaycoke/ec2-gazua) 는 AWS EC2에 쉽게 접속하기 위하여 만들어진 SSH툴 입니다.  
AWS EB, Auto scaling등의 환경에서 잦은 IP주소 변경으로 인하여 서버 접근이 괴로운 인간을 돕기위해 만들어졌습니다.

![screenshot](./image/tty.gif)

## 설치 요구사항 (requirements)

- tmux
- python >= 3.7

## 설치 (installation)

### pip

```bash
$ pip install ec2-gazua
```

### Manually

```bash
$ git clone https://github.com/leejaycoke/ec2-gazua.git
$ cd ./ec2-gazua
$ pip install --user -r requirements.txt 
$ python ec2_gz.py
```

## 필수 설정 (configuration)

`ec2-gz.sample`파일을 ~/.ec2-gz로 복사하시고 편집하세요.

## 설정 (configuration)

`name`은 화면의 제일 왼쪽 그룹에 사용됩니다. AWS 계정이 여러개인 경우 yml문법에 맞게 `---`을 추가하여 사용할 수 있습니다.

```yml
name: my-aws
```

`ssh-path`는 실제 로컬 PC에 ssh key가 저장되어있는 경로입니다. (끝에 /를 붙이지 마세요!)

```yml
ss-path: ~/.ssh
```

`credential`은 AWS 인증 정보입니다. 가능하다면 EC2 ReadOnly 키를 사용하세요.

```yml
credential:
  aws_access_key_id: XXX
  aws_secret_access_key: XXX
  region: ap-northeast-2
```

`group-tag`는 화면의 중간 부분 그룹, `name-tag`는 제일 오른쪽 인스턴스 이름으로 사용됩니다.    
`group-tag`는 여러개의 인스턴스를 그룹으로 묶어주는 역할을 합니다.  
보통 EC2이름을 표현하는데 `Name` Key가 사용되기 때문에 `name-tag`를 수정 할 일은 없을겁니다.   
`group-tag`는 `Team`, `Group`과 같이 의미있는 태그를 만들 필요가 있습니다.

```yml
group-tag: Group
name-tag: Name
```

`filter`를 true로 지정하면 접속 불가능한 instance는 보여주지 않습니다.

- 인스턴스가 가동중이지 않은 경우
- 접속할 수 있는 ssh key가 없습니다.
- 인스턴스에 IP주소를 할당하지 않은경우
- 인스턴스에 private-ip만 할당했지만 `connect-ip`를 public으로 지정한 경우

```yml
filter:
  connectable: false
```

`connect-ip`는 ssh에 접속할 IP주소 유형을 선택합니다. (public|private)  
특정 group혹은 name의 인스턴스의 값을 override할 수 있습니다.  
예를들어 default가 public이지만 특정 group은 private을 사용하고 싶다면  
`그룹명: private`형태로 default값을 override할 수 있습니다.  
마찬가지로 특정 name의 인스턴스는 private을 사용하고 싶다면 `인스턴스명: private`형태로 override할 수 있습니다.  
`group`, `name`은 위에서 지정 한 `group-tag`, `name-tag`에서 설명한 개념과 같습니다.  

```yml
connect-ip:
  default: public
  group:
    live-company-group: private
  name:
    private-my-server: public
```

`key-file`은 ssh에 접속할때 사용할 키 파일명입니다.  
default값을 `auto`로 하신다면 EC2생성시 등록한 키 파일을 ${ssh-path}/${파일명}.pem 경로에서 찾습니다.  
만약 ${파일명}.pem이 존재하지 않는다면 ${ssh-path}/${파일명} (확장자 없음)을 찾게됩니다.  
그래도 키 파일이 존재하지 않는다면 해당 인스턴스는 접속할 수 없습니다.  
만약 default값이 auto가 아닌 `id_rsa`로 입력한다면 `${ssh-path}/id_rsa` 파일을 직접 사용하게 됩니다.  
역시 group과 name을 이용한 override를 지원합니다.

```yml
key-file:
  default: auto
  group:
    was-1: ~/.ssh/test1
  name:
    slave1: ~/.ssh/test2
```

`user`는 ssh에 접속할 사용자 계정을 입력합니다.  
Amazon Linux를 사용한다면 보통 ec2-user가 기본 값이 될 수 있지만  
Linux 배포판, 여러 개발환경에 따라서 변경될 수 있으니 원하시는 계정을 사용해주세요.  
마찬가지로 group, name값을 기반으로 사용자 계정을 override할 수 있습니다.  

```yml
user:
  default: ec2-user
  group:
    my-team: centos
  name:
    web1-instance: leejuhyun
```

## 기타 설정

여러개의 AWS계정을 사용하는 경우 `.ec2-gz`파일 하나에서 아래와 같이 관리할 수 있습니다.

```yml
name: my-aws1
생략
생략

---
name: my-aws2
생략
생략

---
name: my-aws3
생략
```

## License

MIT License

Copyright (c) 2018 JuHyun Lee

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

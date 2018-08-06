# EC2 Gazua

'EC2 가즈아 ~~~!!'는 tmux를 사용하여 여러 EC2 인스턴스에 쉽게 접속할 수 있도록 만들어진 툴 입니다.

![screenshot](./image/tty.gif)

## 설치 요구사항

- tmux
- python 2.x, 3.x
- pip

## 설치 (installation)


```bash
$ git clone https://github.com/leejaycoke/ec2-gazua.git
$ cd ./ec2-gazua
$ pip install --user -r requirements.txt 
$ python ec2-gz.py
```

## 설정 (configuration)

반드시 설정 파일을 만드셔야합니다.

`ec2-gz.sample`파일을 ~/.ec2-gz로 복사하시기 바랍니다.

이제 `~/.ec2-gz`파일을 편집하세요.

> 밑에서 나오게 될 설정 값 Override시 사용되는 group, name태그 명은 equals가 아닌 contains match이므로 모든 글자를 입력할 필요가 없습니다.

```yml
name: my-aws
```

화면의 제일 왼쪽 그룹에 사용됩니다. AWS 계정이 여러개인 경우 yml문법에 맞게 `---`을 추가하여 사용할 수 있습니다.


```yml
ss-path: ~/.ssh
```

ssh key(pem)가 저장되어있는 경로입니다. (끝에 /를 붙이지 마세요!)

```yml
credential:
    aws_access_key_id: XXX
    aws_secret_access_key: XXX
    region: ap-northeast-2
```

AWS 인증 정보입니다. 가능하다면 EC2 ReadOnly 키를 사용하세요.

```yml
group-tag: Group
name-tag: Name
```

`group-tag`는 화면의 중간 부분 그룹, `name-tag`는 제일 오른쪽 인스턴스 이름으로 사용됩니다.

`group-tag`는 여러개의 인스턴스를 그룹으로 묶어주는 역할을 합니다.

EC2에서 사용하는 Tag의 Key를 입력하시면 됩니다.

보통 EC2이름을 표현하는데 `Name` Key가 사용되기 때문에 `name-tag`를 수정 할 일은 없을겁니다.

`group-tag`는 `Team`, `Group`과 같이 의미있는 태그를 만들 필요가 있습니다.

```yml
filter:
    connectable: false
```

이 값이 `true`인 경우 아래 조건에 하나라도 해당되면화면에서 인스턴스를 표시하지 않습니다.

* 인스턴스가 가동중이지 않습니다. (예를들어 terminated된 경우)
* 접속할 수 있는 ssh key(or pem)가 없습니다.
* 접속할 수 있는 IP주소가 없습니다. (예를들어 네트워크 인터페이스가 없는경우, connect-ip설정을 public으로 했지만 인스턴스에 private-ip 인터페이스만 붙어있는 경우)

```yml
connect-ip:
    default: public
    group:
      live-company-group: private
    name:
      private-my-server: public
```

ssh에 접속할 IP주소 유형을 선택합니다. (public|private)

특정 group혹은 name의 인스턴스의 값을 override할 수 있습니다.

예를들어 default가 public이지만 특정 group은 private을 사용하고 싶다면

`그룹명: private`형태로 default값을 override할 수 있습니다.

마찬가지로 특정 name의 인스턴스는 private을 사용하고 싶다면 `인스턴스명: private`형태로 override할 수 있습니다.

`group`, `name`은 위에서 지정 한 `group-tag`, `name-tag`에서 설명한 개념과 같습니다.

```yml
key-file:
    default: auto
    group:
        was-1: ~/.ssh/test1
    name:
        slave1: ~/.ssh/test2
```

ssh에 접속할때 사용할 키 파일명입니다.

default값을 `auto`로 하신다면 EC2생성시 등록한 키 파일을 ${ssh-path}/${파일명}.pem 경로에서 찾습니다.

만약 ${파일명}.pem이 존재하지 않는다면 ${ssh-path}/${파일명} (확장자 없음)을 찾게됩니다.

그래도 키 파일이 존재하지 않는다면 해당 인스턴스는 접속할 수 없습니다.

만약 default값이 auto가 아닌 `id_rsa`로 입력한다면 `${ssh-path}/id_rsa` 파일을 직접 사용하게 됩니다.

역시 group과 name을 이용한 override를 지원합니다.

```yml
user:
    default: ec2-user
    group:
        my-team: centos
    name:
        web1-instance: leejuhyun
```

ssh에 접속할 사용자 계정을 입력합니다.

Amazon Linux를 사용한다면 보통 ec2-user가 기본 값이 될 수 있지만

Linux 배포판, 여러 개발환경에 따라서 변경될 수 있으니 원하시는 계정을 사용해주세요.

마찬가지로 group, name값을 기반으로 사용자 계정을 override할 수 있습니다.

## 기타 설정

여러개의 AWS계정을 사용하는 경우 `.ec2-gz`파일 하나에서 아래와 같이 관리할 수 있습니다.

```
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

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# remote-gazua

리모트-가즈아아ㅏㅏㅏㅏ를 사용하여 ssh를 쉽게 사용해보세요.

- 스크린샷

![screenshot](./image/screen.gif)

## 요구사항

- python2.x, 3.x
- pip
- tmux
- virtualenv

## 문제점

- python v3.x에 대한 대응이 거의 안되어있습니다.

## 개선할 점

- 검색 기능

## 앞으로 추가할 기능

- AWS ec2 불러오기

## 설정

`~/.ssh/config`에 규칙주석을 통해 그룹 설정을 할 수 있습니다.

`#gz:group=원하는 그룹명`을 적어주시면 해당주석의 아래 라인에 있는 Host들은 해당 그룹에 포함되게 됩니다.

예제)

```
#gz:group=live web server

Host live-web1
    HostName 123.123.123.123
    User ec2-user
    IdentityFile ~/.ssh/test1_id_rsa

Host live-web2
    HostName 123.123.123.124
    User ec2-user
    IdentityFile ~/.ssh/test1_id_rsa

#gz:group=live database

Host live-db-master
    HostName 123.123.123.123
    User ec2-user
    IdentityFile ~/.ssh/test2_id_rsa

Host live-db-slave
    HostName 123.123.123.124
    User ec2-user
    IdentityFile ~/.ssh/test2_id_rsa

```

## alias

```bash
$ alias gz='${install_path}/gz'
```
# ec2-gazua

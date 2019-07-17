# test-suite shell script 사용법

## Shell scripts Files

- [clear.sh](#clear.sh)
- [decentralization_test.sh](#decentralization_test.sh)
- [prevote_test.sh](#prevote_test.sh)
- [ready.sh](#ready.sh)
- [reset.sh](#reset.sh)
- [test.sh](#test.sh)

## clear.sh

상태 db, SCORE db, tbears log파일들을 삭제한다.
### Options

None

### example
```bash
$ clear.sh
```

## decentralization_test.sh
탈중앙화에 대한 테스트를 진행

### parameters


| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h      |         | 사용법을 보여준다. |
| -n   |    0     | 테스트 번호. test_decentrailization0.py~test_decentralization6.py 중 선택해서 테스트한다. 기본값:0|
| -a   |    False  | 탈중앙화한 후, 시나리오 테스트를 제외한 모든 테스트 진행|
| -c   |    False     | db를 clear한 후 테스트 진행|
| -d   |    False | 이 플래그가 켜져있다면, test_decentralization0.py ~ test_decentralization6.py 테스트를 한다.|
None

## prevote_test.sh
pre-vote단계의 테스트를 진행

### Options


| shorthand, Name | default | Description                     |
| :-------------- | :------ | :------------------------------ |
| -h      |         | 사용법을 보여준다. |
| -c      |   False      | db를 clear한 후 테스트 진행 |

None

## ready.sh
테스트를 위한 사전작업

### Options

None

## reset.sh
test-suite는 SCOREDB, STATEDB를 .score2, .statedb2에 백업해놓는다. 이 db들을 사용할 수 있도록 한다.

### Options

None

## test.sh
시나리오 테스트를 제외한 모든 테스트를 진행한다.
1. pre-vote 테스트를 진행한다.
2. 탈중앙화 후, t-bears를 재시작하고, 시나리오 테스트를 제외한 모든 테스트를 진행한다.
3. 탈중앙화 후, 시나리오 테스트를 제외한 모든 테스트를 진행한다.
4. 탈중앙화 테스트 코드들을 실행한다.(test_decentralization0 ~ test_decentralization6)

### Options

None

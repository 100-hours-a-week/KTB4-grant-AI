"""표준 라이브러리
"""
import re # 정규식
from pathlib import Path # 경로를 문자열 대신 객체로 다루는 표준 방식

"""외부 라이브러리(pyproject.toml의 dependencies)
"""
import click # cli framework
from rich.console import Console
from rich.table import Table


# 최고 정확도를 추출하는 정규식 패턴
PAT_MAX = re.compile(r"Max accuracy: \s*([\d.]+)%") # check: \s*([\d.]+) 이게 무엇인지
PAT_EMA_MAX = re.compile(r"Max accuracy ema: \s*([\d.]+)%")


def parse_val_acc1(path: Path) -> float | None:
    """log_rank0.txt를 각 실험별로 읽어 해당 실험의 val_acc1의 값을 반환한다.

    파일에서 마지막으로 등장한 "Max accuracy: [acc]%"와 "Max accuracy: [acc_ema]%"의 acc 및 acc_ema를 비교해 더 큰 값을 반환한다.
    """
    last_max_acc: float | None = None
    last_ema_max_acc: float | None = None

    with open(path) as f:
        for line in f: # path 경로의 파일에서 한 줄(line)씩 확인
            # EMA 먼저 시도
            m = PAT_EMA_MAX.search(line)
            if m: # 매칭되면
                last_ema_max_acc = float(m.group(1)) # check: \s*([\d.]+)로부터 나온 것 같은데 `group(1)`이 의미하는 것
                continue

            # EMA 매칭 안되면 원 모델에 대해 시도
            m = PAT_MAX.search(line)
            if m:
                last_max_acc = float(m.group(1))
    
    # 파일 모두 확인 후 None을 걸러내고 둘 중 큰 값을 반환
    accs = [acc for acc in (last_max_acc, last_ema_max_acc) if acc is not None] # None 거름망
    return max(accs) if accs else None # 최댓값 혹은 None 반환

def discover(root: Path) -> list[tuple[str, Path, float | None]]:
    """root directory 바로 아래에 있는 각 실험들을 찾아 (이름, 경로, val_acc1)을 tuple로 반환"""
    out = []

    for d in sorted(root.iterdir()): # iterdir(): root 바로 아래 항목들을 Path 객체로 나열
        if not d.is_dir(): # directory 확인
            continue

        log = d / "log_rank0.txt" # pathlib의 '/' 연산자: OS에 무관하게 경로를 이음
        if not log.exists(): # log가 있는지 확인
            continue

        out.append((d.name, d, parse_val_acc1(log)))
    
    return out

"""click의 group: subcommand를 묶는 상위 명령. cli 자체는 아무 일도 하지 않고, subcommand(`summary`/`best`)로 분기만
"""
@click.group()
def cli():
    pass

"""`summary` command: 모든 실험의 val_acc1을 표로 출력"""
@cli.command()
@click.argument(
    "root", # root 경로
    # click.Path: parameter 검증
    #   exists: root 경로가 있는지 확인
    #   file_okay: directory만 받을 수 있게 확인
    #   path_type: 문자열 경로를 Path 객체로 바꿔 전달
    type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def summary(root: Path):
    # 표 생성
    table = Table(title="Exps")
    table.add_column("Name")
    table.add_column("Top-1 Acc (%)")
    table.add_column("path")

    # discover 함수를 통해 root 경로에서의 실험 결과 받아오기
    for name, path, acc in discover(root):
        table.add_row(
            name,
            f"{acc:.2f}" if acc is not None else "-", # None일 경우 '-'로 처리
            str(path)
        )
    
    # 표 출력
    Console().print(table)

"""`best` command: 모든 실험 중 가장 높은 val_acc1 결과를 출력"""
@cli.command()
@click.argument(
    "root",
    type=click.Path(exists=True, file_okay=False, path_type=Path)
)
def best(root: Path):
    exps = [exp for exp in discover(root) if exp[2] is not None] # val_acc1이 None이 아닌 경우에 한해 정보를 받기

    if not exps: # 유효한 실험이 없으면 에러 발생
        raise click.ClickException("No experiments with val_acc1")
    
    name, path, acc = max(exps, key=lambda exp: exp[2]) # 가장 높은 val_acc1의 정보 가져오기

    Console().print(f"[bold green]{name}[/]\tTop-1 Acc (%)={acc:.2f}\tpath={path}") # rich의 마크업 문법
# aegis-dataset-prep

AEGIS 비전-언어 실험 노트북을 위한 데이터셋 준비, 파인튜닝, 업로드,
평가 작업 공간입니다.

## 현재 구현됨 (Currently implemented)

- `Qwen3-VL-2B-Finetuning-Eval.ipynb`: gated dataset 로드, train/test split 준비,
  LoRA 파인튜닝, 모델 artifact 업로드, 예측 평가를 한 흐름으로 실행하는
  노트북입니다.
- `src/aegis_dataset_prep/`: 환경 설정, Hugging Face cache 설정, dataset
  split/count, chat 변환, pickle IO, plotting, 출력 parsing/metric 계산을 위한
  재사용 helper입니다.
- `tests/`: 재사용 helper용 lightweight unit test와, 커밋된 노트북에 cell output
  또는 execution count가 남아 있으면 실패하는 청결성 검사입니다.
- `.github/workflows/ci.yml`: GPU/ML training stack을 설치하지 않고 lightweight
  test만 실행하는 GitHub Actions workflow입니다.

## 계획됨 (Planned)

- runtime 환경이 충분히 안정되면 training/upload orchestration도 명시적인 script
  entrypoint 뒤로 옮깁니다. 지금은 노트북 밖에서 해당 경로를 검증할 수 있는
  범위까지만 분리했습니다.

## 설계 의도 (Design intent)

- 무거운 모델 학습, 인증, 업로드, checkpoint sync는 명시적인 노트북 실행 단계로
  남깁니다.
- parsing, 변환, config, count처럼 순수하게 검토 가능한 로직은 import 가능한
  module로 분리해 GPU 접근이나 private credential 없이도 review/test할 수 있게
  합니다.

## 하지 않는 것 (Non-goals)

- 이 repository는 model weight, dataset, credential, run link, account ID,
  local runtime output을 공개하지 않습니다.
- CI workflow는 `unsloth`, CUDA-specific `torch` 설치나 fine-tuning/evaluation
  실행을 시도하지 않습니다.

## 비공개 처리 (Redacted)

- Dataset ID, model destination, Hugging Face token, W&B credential, account
  identifier, 실행된 인증 output은 git history 밖에 둡니다.

## 안전한 설정

1. 이 repository 밖에 격리된 Python environment를 만듭니다.
2. runtime-specific GPU stack을 먼저 설치한 뒤 `pip install -r requirements.txt`를
   실행합니다.
3. `.env.example`을 private runtime 설정으로 복사하고 값은 local에서만 채웁니다.
4. training, sync, upload cell을 실행하기 전에 첫 번째 notebook cell을 검토합니다.
   필요한 설정은 experiment name, base model, dataset, output model destination,
   LoRA rank, batch size입니다.

## 로컬 검사

training stack 없이 lightweight check만 실행합니다.

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## 로컬 output

생성된 checkpoint, run log, 변환된 dataset, local cache, notebook checkpoint는
`.gitignore`로 제외합니다. 큰 artifact와 private credential은 git history 밖에
둡니다.

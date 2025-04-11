# 심화과제 - Pre-trained 모델로 효율적인 NLP 모델 학습하기

## Q1) 어떤 task를 선택하셨나요?
> MNLI task


## Q2) 모델은 어떻게 설계하셨나요? 설계한 모델의 입력과 출력 형태가 어떻게 되나요?
> MNLI 단순한 언어 이해 능력만을 필요하기 때문에 사전학습된 DistilBERT를 활용하였습니다. DistilBERT는 기존 BERT 모델을 경량화한 버전으로, 성능은 유지하면서 파라미터 수를 줄인 모델입니다.

> 모델의 설계는 다음과 같습니다:
> 1. 사전학습된 DistilBERT를 인코더로 사용하고, 분류 태스크를 위한 Linear layer를 추가하였습니다.
> 2. DistilBERT의 파라미터는 고정(freeze)하고 분류 레이어만 학습하는 방식으로 fine-tuning을 진행했습니다.

> 입력 형태:
> - 두 문장(premise, hypothesis)을 연결하여 하나의 시퀀스로 만든 후 토큰화합니다. 
> - 최대 길이 400의 input_ids 형태로 변환됩니다.
> - 입력 shape: (batch_size, sequence_length)

> 출력 형태:
> - 3개 클래스(0, 1, 2)에 대한 로짓(logit) 값을 출력합니다.
> - 출력 shape: (batch_size, 3)
> - 추론 시에는 argmax를 통해 가장 높은 점수의 클래스를 선택합니다.


## Q3) 실제로 pre-trained 모델을 fine-tuning했을 때 loss curve은 어떻게 그려지나요? 그리고 pre-train 하지 않은 Transformer를 학습했을 때와 어떤 차이가 있나요? 
> 사전학습된 DistilBERT 모델을 fine-tuning 했을 때:
> - Loss curve는 초기 33.14에서 시작하여 점진적으로 감소하여 50 epoch 후 약 29.93까지 감소했습니다.
> - 학습 정확도는 0.612, 테스트 정확도는 0.426으로 일정 수준의 일반화 성능을 보여주었습니다.
> - Loss 감소가 안정적이며 큰 진폭 없이 꾸준히 학습되는 패턴을 보입니다.

> Pre-train 하지 않은 Transformer 모델과의 차이점:
> - 사전학습하지 않은 Transformer는 학습 초기부터 수렴하는 데 더 오랜 시간이 걸리며, 초기 손실이 더 높습니다.
> - 주어진 데이터셋 크기로는 일반화 성능이 크게 떨어집니다(week2/basic/Transformer.ipynb 결과 참조: 학습 정확도 0.083, 테스트 정확도 0.030).
> - 사전학습 모델은 이미 언어의 구조와 의미를 학습하고 있어 fine-tuning만으로도 상대적으로 높은 정확도를 달성할 수 있습니다.
> - 테스트 셋에 대한 일반화 능력에서 사전학습 모델(test acc: 0.426)이 일반 Transformer(test acc: 0.030)보다 훨씬 우수합니다.
> - 동일한 태스크에 대해 사전학습 모델은 훨씬 적은 에포크 수로도 더 높은 성능을 달성할 수 있습니다.
- 
-  
-  
- 이미지 첨부시 : ![이미지 설명](경로) / 예시: ![poster](./image.png)

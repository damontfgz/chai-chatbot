FROM rayproject/ray:2.46.0

COPY finetune.py /finetune.py

ENV PYTHONUNBUFFERED 1

CMD python3 /finetune.py --device cuda
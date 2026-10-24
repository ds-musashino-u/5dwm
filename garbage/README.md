# Garbage Density

写真内のゴミ個数・曖昧候補・推定面積・Garbage Density（個/m²）をJSONで出力します。
Density = ゴミ個数 ÷ 推定面積。

## セットアップ

Python 3.9で、このフォルダを作業ディレクトリにして実行します。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` の `OPENAI_API_KEY` を設定します。

## 実行

```bash
python estimate_garbage_index.py /path/to/photo.jpg
```

Deep Anything 3（CPU）を併用する場合は、Gitを用意し、追加で実行します。

```bash
python -m pip install -r requirements-depth.txt
python -m pip install --no-deps "git+https://github.com/ByteDance-Seed/Depth-Anything-3.git@41736238f5bced4debf3f2a12375d2466874866d"
python generate_depth_anything3.py /path/to/photo.jpg
python estimate_garbage_index.py /path/to/photo.jpg --use-depth-anything
```

ゴミ個数はRGBのみで判定し、Depth Anythingの深度画像・統計は面積推定を補助します。
DA3-SMALLは相対深度なので、面積とDensityは概算です。画像はOpenAI APIに送信されます。

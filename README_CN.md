# KYC OCR Finder

在 macOS 本地扫描 KYC 图片和 PDF，按身份证号或姓名查找资料。原始文件只读，不会被修改。

## 前置条件

安装 Tesseract：

```bash
brew install tesseract
```

## 最常用命令

进入该工具文件夹后运行：

```bash
python3 find_kyc.py \
  --root "$HOME/Desktop/upay/kyc" \
  --id "950926-10-5877" \
  --name "HASIM HAIRUL AIMAN ASYRAF BIN" \
  --workers 4
```

结果显示在终端，并写入当前文件夹的 `ocr_matches.txt`。

## 扫描横放/倒置的证件

加上 `--rotate` 会额外尝试四个旋转方向，更可靠，但大约会慢四倍：

```bash
python3 find_kyc.py \
  --root "$HOME/Desktop/upay/kyc" \
  --id "950926-10-5877" \
  --name "HASIM HAIRUL AIMAN ASYRAF BIN" \
  --rotate
```

## 仅按证件号搜索

```bash
python3 find_kyc.py --root "$HOME/Desktop/upay/kyc" --id "950926105877"
```

## GitHub 注意事项

`.gitignore` 已排除 KYC 原件、OCR 匹配结果和临时文件。不要把真实证件文件或包含 OCR 内容的结果提交到 GitHub。

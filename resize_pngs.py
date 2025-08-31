import os
from PIL import Image
import shutil
import numpy as np

def trim_transparent_edges(img: Image.Image) -> Image.Image:
    """
    PillowのImageオブジェクトを受け取り、縁の透過部分を正確に切り取る。
    NumPyを使いピクセルを直接解析するため、getbbox()よりも堅牢。
    
    Args:
        img: 処理対象のPillow Imageオブジェクト。
        
    Returns:
        縁の透過部分を切り取ったPillow Imageオブジェクト。
    """
    # PillowイメージをNumPy配列に変換
    # RGBAモードでない場合も想定し、変換をかけてアルファチャンネルを確保
    np_img = np.array(img.convert('RGBA'))
    
    # アルファチャンネル（4番目のチャンネル）のデータを取得
    alpha_channel = np_img[:, :, 3]
    
    # 透明ではないピクセル（アルファ > 0）が存在する行と列を探す
    non_transparent_rows = np.where(np.any(alpha_channel > 0, axis=1))[0]
    non_transparent_cols = np.where(np.any(alpha_channel > 0, axis=0))[0]
    
    # 画像が完全に透明な場合は、何もせず元の画像を返す
    if not (non_transparent_rows.any() and non_transparent_cols.any()):
        return img
        
    # 透明でない領域の上下左右の境界を特定
    top, bottom = non_transparent_rows[0], non_transparent_rows[-1]
    left, right = non_transparent_cols[0], non_transparent_cols[-1]
    
    # Pillowのcrop用に(left, top, right, bottom)の形式で座標を作成
    # NumPyのインデックスは包括的なので、右と下の座標に+1する
    bbox = (left, top, right + 1, bottom + 1)
    
    # 計算した境界で画像を切り抜いて返す
    return img.crop(bbox)


def resize_replace_and_backup(
    target_folder: str, 
    backup_folder: str, 
    target_width: int, 
    target_height: int
):
    """
    指定フォルダ内のPNG画像の透過の縁を切り取ってからリサイズし、
    元のファイルは別フォルダにバックアップする。
    """
    # 1. 各フォルダの存在確認と作成
    if not os.path.isdir(target_folder):
        print(f"[エラー] 対象フォルダが見つかりません: {target_folder}")
        return
        
    if not os.path.isdir(backup_folder):
        os.makedirs(backup_folder)
        print(f"[情報] バックアップ用フォルダを作成しました: {backup_folder}")

    # 2. フォルダ内のPNGファイルを取得
    try:
        png_files = [f for f in os.listdir(target_folder) if f.lower().endswith('.png')]
        if not png_files:
            print(f"[情報] フォルダ内に処理対象のPNGファイルが見つかりませんでした: {target_folder}")
            return
        print(f"[情報] {len(png_files)}個のPNGファイルを処理します...")
    except Exception as e:
        print(f"[エラー] ファイルリストの取得中にエラーが発生しました: {e}")
        return

    # 3. 各ファイルを順番に処理
    for filename in png_files:
        original_path = os.path.join(target_folder, filename)
        backup_path = os.path.join(backup_folder, filename)
        
        try:
            # 1. まず、元のファイルをバックアップフォルダに移動
            shutil.move(original_path, backup_path)

            # 2. バックアップした画像を開いて処理
            with Image.open(backup_path) as img:
                
                # ▼▼▼【改善ポイント】新しい切り取り関数を呼び出す ▼▼▼
                # 2a. 縁の透過部分を正確に切り取る
                trimmed_img = trim_transparent_edges(img)
                
                # 3. 切り取り後の画像をリサイズ
                resized_img = trimmed_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 4. リサイズ後の画像を、元のファイルパスに保存
                resized_img.save(original_path)
                
            print(f"  - 処理完了: {filename} -> 縁の透過を切り取り後リサイズし、元ファイルをバックアップしました。")

        except Exception as e:
            print(f"  - [エラー] {filename} の処理中にエラーが発生しました: {e}")

    print("\n[成功] すべての処理が完了しました。")


# --- 設定項目 ---
TARGET_FOLDER = "original_pngs"
BACKUP_FOLDER = "used_pngs"


TARGET_WIDTH = 1290
TARGET_HEIGHT = 2796

# --- 実行 ---
resize_replace_and_backup(TARGET_FOLDER, BACKUP_FOLDER, TARGET_WIDTH, TARGET_HEIGHT)



''' iPhone
TARGET_WIDTH = 1290
TARGET_HEIGHT = 2796
'''
''' iPad
TARGET_WIDTH = 2752
TARGET_HEIGHT = 2064
'''



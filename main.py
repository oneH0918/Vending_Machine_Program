import tkinter as tk
from tkinter import messagebox

# 初期値
# 商品リスト
list_items = [
    ["コーラ", 160],
    ["ファンタオレンジ", 160],
    ["ファンタグレープ", 160],
    ["天然水", 120],
    ["いろはす", 150],
    ["りんごジュース", 150],
    ["オレンジジュース", 150],
    ["ぶどうジュース", 150],
    ["コーヒー", 150],
    ["いろはすみかん", 150],
    ["抹茶ラテ", 160],
]
stock = [10 for _ in range(len(list_items))]  # 各商品の在庫数 (初期値---10本)
deposited_money = 0  # 投入金額を初期化
selected_items = {}  # 選択中の商品を初期化
purchased_items_window = None  # 購入商品ウィンドウを初期化
total_sales = 0 #売上金額を格納する変数
total_sales_label = None

def deposit():
    # 入金ダイアログ
    def deposit_dialog():
        # ダイアログウィンドウ
        dialog = tk.Toplevel(root)
        dialog.title("入金")
        dialog.geometry("300x200")
        dialog.resizable(width=False, height=False)

        # 金額入力
        label_amount = tk.Label(dialog, text="金額を入力してください")
        label_amount.pack(pady=20)
        entry_amount = tk.Entry(dialog)
        entry_amount.pack()

        # 確定ボタン
        def confirm_deposit():
            try:
                amount = int(entry_amount.get())  # 入力値を整数に変換
                if amount > 0:
                    update_money_display(amount)  # 投入金額表示を更新
                    dialog.destroy()  # ダイアログを閉じる
                else:
                    messagebox.showerror("エラー", "有効な金額を入力してください")
            except ValueError:
                messagebox.showerror("エラー", "数値を入力してください")

        button_confirm = tk.Button(dialog, text="確定", command=confirm_deposit)
        button_confirm.pack(pady=20)

    deposit_dialog()

def update_money_display(amount):
    global deposited_money  # 投入金額をグローバル変数で管理
    deposited_money += amount
    canvas_money.delete("all")  # キャンバスの内容をクリア
    canvas_money.create_text(100, 50, text=f"{deposited_money}円", font=("Arial", 20))

def refund():
    global deposited_money
    if deposited_money == 0:
        messagebox.showinfo("返金", "投入金額はありません")
        return

    change = calculate_change(deposited_money)
    show_refund_dialog(change)

    deposited_money = 0
    update_money_display(0)

def calculate_change(amount):
    # お札・硬貨の種類と枚数を計算
    money_types = [10000, 5000, 1000, 500, 100, 50, 10, 1]
    change = {}
    remaining_amount = amount

    for money in money_types:
        change[money] = remaining_amount // money
        remaining_amount %= money

    return change

def show_refund_dialog(change):
    # 返金内容を表示するダイアログ
    dialog = tk.Toplevel(root)
    dialog.title("返金")
    dialog.geometry("300x400")

    cancel_items()

    label_message = tk.Label(dialog, text="返金された金額")
    label_message.pack(pady=10)

    listbox = tk.Listbox(dialog)
    listbox.pack(fill=tk.BOTH, expand=True)

    total_refund = 0  # 合計返金額を計算するための変数
    for money, count in change.items():
        if count > 0:
            listbox.insert(tk.END, f"{money}円: {count}枚")
            total_refund += money * count  # 合計返金額を計算
    listbox.insert(tk.END, "")
    listbox.insert(tk.END, f"計: {total_refund}円")

    button_close = tk.Button(dialog, text="閉じる", command=dialog.destroy)
    button_close.pack(pady=10)

def buy():
    global deposited_money, purchased_items_window, total_sales
    total_price = 0
    # 在庫不足フラグ
    out_of_stock = False
    out_of_stock_message = ""

    # 選択された商品の合計金額を計算
    for item_name, quantity in selected_items.items():
        for i, item in enumerate(list_items):
            if item[0] == item_name:
                if stock[i] < quantity:
                    # 在庫が足りない場合
                    out_of_stock = True
                    out_of_stock_message += f"{item_name}の在庫が不足しています。\n"
                total_price += item[1] * quantity
                break

    # **商品が選択されているかチェック**
    if not selected_items:
        # 商品が選択されていない場合
        messagebox.showerror("エラー", "商品を選択してください。")
    elif out_of_stock:
        # 在庫が足りない商品がある場合
        messagebox.showerror("エラー", out_of_stock_message)
    elif deposited_money < total_price:
        # 投入金額が足りない場合
        messagebox.showerror("エラー", f"投入金額が{total_price - deposited_money}円不足しています。")
    else:
        # 投入金額が足りる場合
        deposited_money -= total_price
        update_money_display(0)

        # 売上金額を更新
        total_sales += total_price  # 売上金額を加算
        update_total_sales()  # 売上金額表示を更新

        # 在庫を減らす
        for item_name, quantity in selected_items.items():
            for i, item in enumerate(list_items):
                if item[0] == item_name:
                    if stock[i] >= quantity:  # 在庫数が十分にある場合のみ減らす
                        stock[i] -= quantity
                    break

        # **購入された商品の情報をコピーしておく**
        purchased_items = selected_items.copy()

        # 商品選択をリセット
        cancel_items()

        # 商品ステータスを更新
        update_item_status()

        # 購入商品ウィンドウを更新
        if purchased_items_window is not None:
            purchased_items_window.destroy() # ウィンドウを削除

        # **コピーした購入商品を表示**
        show_purchased_items(purchased_items, total_price)

def update_total_sales():
    global total_sales_label
    # 売上金額表示を更新
    # total_sales_label が存在する場合のみ更新
    if total_sales_label is not None:  
        total_sales_label.config(text=f"現在の売上金額: {total_sales}円")

def update_item_status():
    # 商品ステータスを更新
    for i, item in enumerate(list_items):
        frame = frame_items.winfo_children()[i]  # i番目の商品フレームを取得
        label_status = frame.winfo_children()[3]  # 商品ステータスラベルを取得
        if stock[i] > 0:
            label_status.config(text="在庫あり", fg="green")
        else:
            label_status.config(text="売り切れ", fg="red")

def show_purchased_items(purchased_items, total_price):
    # 購入された商品を表示するウィンドウ
    global purchased_items_window

    purchased_items_window = tk.Toplevel(root)
    purchased_items_window.title("購入商品")
    purchased_items_window.geometry("300x400")

    label_message = tk.Label(purchased_items_window, text="購入された商品")
    label_message.pack(pady=10)

    listbox = tk.Listbox(purchased_items_window)
    listbox.pack(fill=tk.BOTH, expand=True)

    for item_name, quantity in purchased_items.items():
        listbox.insert(tk.END, f"{item_name} x {quantity}")
    listbox.insert(tk.END, "")
    listbox.insert(tk.END, f"計: {total_price}円")

    button_close = tk.Button(purchased_items_window, text="閉じる", command=purchased_items_window.destroy)
    button_close.pack(pady=10)

# ウィンドウの作成
root = tk.Tk()
root.geometry("900x1000")
root.title("自動販売機")
root.resizable(width=False, height=False)

# メインキャンバス
canvas_main = tk.Canvas(root, width=900, height=1000)
canvas_main.place(x=0, y=0)

# 選択中の商品の表示
frame_select_items = tk.Frame(canvas_main, width=600, height=300, relief=tk.GROOVE, bd=4)
frame_select_items.place(x=50, y=650)

# スクロールバーを作成
scrollbar = tk.Scrollbar(frame_select_items, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # スクロールバーを右側に配置

#  frame_select_items の中に canvas_select_items を作成
canvas_select_items = tk.Canvas(frame_select_items, width=580, height=300) # スクロールバー分の幅を引く
canvas_select_items.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# canvas_select_items にスクロールバーを設定
canvas_select_items.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=canvas_select_items.yview)

# 選択中の商品を格納する辞書
selected_items = {}

def update_select_items(item_name, quantity_change):
    global selected_items
    if item_name in selected_items:
        selected_items[item_name] += quantity_change
        if selected_items[item_name] <= 0:
            del selected_items[item_name]
    elif quantity_change > 0:
        selected_items[item_name] = quantity_change

    # canvas_select_itemsの内容をクリア
    canvas_select_items.delete("all")

    # 選択中の商品を表示
    y = 10
    for item_name, quantity in selected_items.items():
        canvas_select_items.create_text(20, y, text=f"{item_name} x {quantity}", anchor=tk.W, font=("Arial", 14))
        y += 20

    # スクロール範囲を更新
    canvas_select_items.config(scrollregion=canvas_select_items.bbox("all"))

# 商品の表示
frame_items = tk.Frame(canvas_main, width=600, height=300, relief=tk.GROOVE, bd=4)
frame_items.place(x=50, y=50)

# **ここから商品ブロックの作成と配置**
for i, item in enumerate(list_items):
    # 各商品ブロックを作成
    item_frame = tk.Frame(frame_items, width=100, height=100, relief=tk.RAISED, bd=2)
    item_frame.grid(row=i // 9, column=i % 9, padx=5, pady=5)  # 5列に並べる

    # 商品画像 (ここではラベルで代用)
    label_image = tk.Label(item_frame, text=f"商品画像{i+1}")
    label_image.grid(row=0, column=0, sticky="nsew")

    # 商品名
    label_name = tk.Label(item_frame, text=item[0])
    label_name.grid(row=1, column=0, sticky="nsew")

    # 値段
    label_price = tk.Label(item_frame, text=f"{item[1]}円")
    label_price.grid(row=2, column=0, sticky="nsew")

    # 商品ステータス
    if stock[i] > 0:  # 在庫がある場合
        label_status = tk.Label(item_frame, text="在庫あり", fg="green")  # 文字色を緑に設定
    else:  # 在庫がない場合
        label_status = tk.Label(item_frame, text="売り切れ", fg="red")  # 文字色を赤に設定
    label_status.grid(row=3, column=0, sticky="nsew")

    # 数量増減ボタン
    button_frame = tk.Frame(item_frame)  # ボタンを格納するフレームを作成
    button_frame.grid(row=4, column=0) # フレームを拡張して中央に配置

    button_minus = tk.Button(button_frame, text="-", command=lambda name=item[0]: update_select_items(name, -1))
    button_minus.pack(side=tk.LEFT)

    button_plus = tk.Button(button_frame, text="+", command=lambda name=item[0]: update_select_items(name, 1))
    button_plus.pack(side=tk.RIGHT)

# 投入金額の表示
frame_money = tk.Frame(canvas_main, width=200, height=100, relief=tk.GROOVE, bd=4)
frame_money.place(x=50, y=500)
canvas_money = tk.Canvas(frame_money, width=200, height=100)
canvas_money.pack()

# 入金ボタン
deposited_money = 0  # 投入金額を初期化
btn_deposit=tk.Button(canvas_main, text="入金", width=10, height=2, command=deposit)
btn_deposit.place(x=280, y=530)

# 返金ボタン
btn_refund = tk.Button(canvas_main, text="返金", width=10, height=2, command=refund)  # 返金処理を追加
btn_refund.place(x=380, y=530)

# 購入ボタン
btn_buy = tk.Button(canvas_main, text="購入", width=10, height=5, command=buy)  # コマンドを設定
btn_buy.place(x=750, y=800)

# 商品取り消しボタンが押された時の処理
def cancel_items():
    global selected_items
    selected_items = {}  # 選択中の商品をクリア
    canvas_select_items.delete("all")  # キャンバスの内容をクリア
    canvas_select_items.config(scrollregion=canvas_select_items.bbox("all"))  # スクロール範囲を更新

# 商品取消しボタン
btn_items_cancel = tk.Button(canvas_main, text="商品取消し", width=8, height=2, command=cancel_items)  # コマンドを設定
btn_items_cancel.place(x=660, y=650) 

#------------------
def show_stock_window():
    global stock_window, total_sales_label

    # 在庫管理ウィンドウを作成
    stock_window = tk.Toplevel(root)
    stock_window.title("在庫管理")
    stock_window.geometry("500x700")  # ウィンドウサイズをさらに広げる

    # 在庫状況を表示するフレームを作成
    stock_frame = tk.Frame(stock_window)
    stock_frame.pack(fill=tk.BOTH, expand=True)

    # チェックボックスの値を格納するリスト
    checkbox_vars = [tk.BooleanVar() for _ in range(len(list_items))]

    # 在庫数のラベルを保存するリスト
    stock_labels = []

    # 売上金額表示用のフレーム
    sales_frame = tk.Frame(stock_window)
    sales_frame.pack(pady=10)

    # 売上金額表示用のラベル
    total_sales_label = tk.Label(sales_frame, text=f"現在の売上金額: {total_sales}円", font=("Arial", 16))
    total_sales_label.pack()

    # 各商品の在庫状況を表示
    for i, item in enumerate(list_items):
        # 商品名と在庫数を表示するフレーム
        item_frame = tk.Frame(stock_frame)
        item_frame.pack(fill=tk.X, padx=10, pady=5, anchor=tk.CENTER)  # 中央揃え

        # 商品名と在庫数のラベル
        label_stock = tk.Label(item_frame, text=f"{item[0]}: {stock[i]}本", width=20)
        label_stock.pack(side=tk.LEFT)
        stock_labels.append(label_stock)

        # 補充ボタン
        replenish_button = tk.Button(item_frame, text="補充", command=lambda index=i: replenish_item(index))
        replenish_button.pack(side=tk.LEFT, padx=5)

        # チェックボックス
        checkbox = tk.Checkbutton(item_frame, variable=checkbox_vars[i])
        checkbox.pack(side=tk.LEFT)

    # 一括補充数の入力フレーム
    bulk_frame = tk.Frame(stock_window)
    bulk_frame.pack(pady=10)

    label_bulk = tk.Label(bulk_frame, text="一括補充数:")
    label_bulk.pack(side=tk.LEFT)

    entry_bulk = tk.Entry(bulk_frame)
    entry_bulk.pack(side=tk.LEFT)

    # 一括補充ボタンを作成する前に bulk_replenish 関数を定義
    def bulk_replenish():
        try:
            amount = int(entry_bulk.get())  # 入力値を整数に変換
            if amount > 0:
                for i, var in enumerate(checkbox_vars):
                    if var.get():  # チェックボックスがオンになっている場合
                        stock[i] += amount  # 在庫数を増やす
                        # 在庫数ラベルを更新
                        stock_labels[i].config(text=f"{list_items[i][0]}: {stock[i]}本")
                update_item_status()  # 商品ステータスを更新
            else:
                messagebox.showerror("エラー", "有効な数量を入力してください")
        except ValueError:
            messagebox.showerror("エラー", "数値を入力してください")

    # 一括補充ボタン
    bulk_button = tk.Button(stock_window, text="一括補充", command=bulk_replenish)
    bulk_button.pack(pady=10)

    # 閉じるボタンを作成
    close_button = tk.Button(stock_window, text="閉じる", command=stock_window.destroy)
    close_button.pack(pady=10)

    # replenish_item 関数を定義
    def replenish_item(index):
        def replenish_dialog():
            # ダイアログウィンドウ
            dialog = tk.Toplevel(root)
            dialog.title("補充")
            dialog.geometry("300x200")
            dialog.resizable(width=False, height=False)

            # 数量入力
            label_amount = tk.Label(dialog, text="補充する数量を入力してください")
            label_amount.pack(pady=20)
            entry_amount = tk.Entry(dialog)
            entry_amount.pack()

            # 確定ボタン
            def confirm_replenish():
                try:
                    amount = int(entry_amount.get())  # 入力値を整数に変換
                    if amount > 0:
                        stock[index] += amount  # 在庫数を増やす
                        update_item_status()  # 商品ステータスを更新
                        # 在庫数ラベルを更新
                        stock_labels[index].config(text=f"{list_items[index][0]}: {stock[index]}本")
                        dialog.destroy()  # ダイアログを閉じる
                    else:
                        messagebox.showerror("エラー", "有効な数量を入力してください")
                except ValueError:
                    messagebox.showerror("エラー", "数値を入力してください")

            button_confirm = tk.Button(dialog, text="確定", command=confirm_replenish)
            button_confirm.pack(pady=20)

        replenish_dialog()


#管理ボタン
btn_settings = tk.Button(canvas_main, text="管理", width=4, height=1, command=show_stock_window)  # コマンドを設定
btn_settings.place(x=850, y=10)

# 投入金額の初期表示
update_money_display(0)  # 0円を表示

root.mainloop()
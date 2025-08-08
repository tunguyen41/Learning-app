from tkinter import *
from tkinter import ttk, messagebox

import psycopg2

root = Tk()
root.title("Spaced-Repetition Vocabulary App")
root.geometry("900x700")
root.configure(bg="#f5f5f5")

def mainMenu():
    for widget in root.winfo_children():
        widget.destroy()

    title = Label(root, text="Spaced-Repetition System", font=("Helvetica", 24, "bold"), bg="#f5f5f5", fg="#333")
    title.pack(pady=30)

    frame1 = Frame(root, bg="#f5f5f5")
    frame1.pack(pady=10)

    buttons = [
        ("📖 Word List", wordList),
        ("📆 Day 2", day_2),
        ("📆 Day 4", day_4),
        ("📆 Day 7", day_7),
        ("📆 Day 12", day_12),
        ("📆 Day 21", day_21)
    ]
    for i, (text, command) in enumerate(buttons):
        btn = Button(frame1, text=text, command=command,
                     width=15, height=3, font=("Helvetica", 12, "bold"),
                     bg="#4CAF50", fg="white", bd=0, relief=RAISED, activebackground="#388E3C")
        btn.grid(row=i//3, column=i%3, sticky="ew", padx=15, pady=15)

def wordList():
    for widget in root.winfo_children():
        widget.destroy()



    #User action
    def insert_word():
        query = 'insert into Vocabulary("Word", "Meaning", "Example in French", "Example in English","Start date") values (%s, %s, %s, %s, %s)'
        parameters = (word_entry.get(), meaning_entry.get(), fexam_entry.get(), eexam_entry.get(), date_entry.get())
        run_query(query, parameters)
        refresh_treeview(tree, treeview_query)
        messagebox.showinfo("Information", "Data inserted successfully")

    def delete_word():
        selected_item = tree.selection()[0]
        word_id = tree.item(selected_item)['values'][0]
        query = "delete from vocabulary where \"ID\" = %s"
        parameters = (word_id,)
        run_query(query, parameters)
        refresh_treeview(tree, treeview_query)
        messagebox.showinfo("Information", "Data deleted successfully")

    def update_word():
        selected_item = tree.selection()[0]
        word_id = tree.item(selected_item)['values'][0]

        set_clause, parameters = get_values()
        query = f'update vocabulary set {set_clause} where "ID" = %s'
        parameters.append(word_id)
        run_query(query, tuple(parameters))
        refresh_treeview(tree, treeview_query)
        messagebox.showinfo("Information", "Data updated successfully")

    def get_values():
        set_clause_parts = []
        parameters = []
        for entry, name in zip(entries, labels):
            value = entry.get()
            if value != "":
                set_clause_parts.append(f'"{name}" = %s')
                parameters.append(value)
        set_clause = ",".join(set_clause_parts)

        return set_clause, parameters

    title = Label(root, text="📚 Word Management", font=("Helvetica", 22, "bold"), bg="#f5f5f5")
    title.pack(pady=20)

    frame = Frame(root, bg="#f5f5f5")
    frame.pack(pady=10)

    labels = ["Word", "Meaning","Example in French", "Example in English", "Start date"]
    entries = []

    for i, text in enumerate(labels):
        Label(frame, text=text + ":", font=("Helvetica", 12), bg="#f5f5f5").grid(row=i, column=0, sticky=W, padx=5,
                                                                                      pady=5)
        entry = Entry(frame, width=40, font=("Helvetica", 12))
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    word_entry, meaning_entry, fexam_entry, eexam_entry, date_entry = entries

    # Button to change
    button_frame = Frame(root, bg="#f5f5f5")
    button_frame.pack(pady=10)

    Button(button_frame, text="Add", width=10, bg="#2196F3", fg="white", font=("Helvetica", 11),
           command=insert_word).grid(row=0, column=0, padx=10)
    Button(button_frame, text="Update", width=10, bg="#FFC107", fg="white", font=("Helvetica", 11),
           command=update_word).grid(row=0, column=1, padx=10)
    Button(button_frame, text="Delete", width=10, bg="#F44336", fg="white", font=("Helvetica", 11),
           command=delete_word).grid(row=0, column=2, padx=10)
    Button(button_frame, text="Back", width=10, bg="#9E9E9E", fg="white", font=("Helvetica", 11),
           command=mainMenu).grid(row=0, column=3, padx=10)

    # Table
    tree_frame = Frame(root)
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side= RIGHT, fill = Y)

    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    tree.pack(fill=BOTH, expand=True)
    tree_scroll.config(command=tree.yview)

    tree['columns'] = ("id", "word", "meaning", "example_in_french", "example_in_english", "start_date")
    tree.column("#0", width=0, stretch=NO)
    tree.heading("id", text="ID")
    tree.heading("word", text="Word")
    tree.heading("meaning", text="Meaning")
    tree.heading("example_in_french", text="Example in French")
    tree.heading("example_in_english", text="Example in English")
    tree.heading("start_date", text="Start Date")

    for col in tree['columns']:
        tree.column(col, anchor=CENTER, width=120)

    treeview_query = 'select * from vocabulary;'
    refresh_treeview(tree, treeview_query)

def review_day(day = ""):
    for widget in root.winfo_children():
        widget.destroy()
    def check_to_reset():
        global wrong_times
        wrong_times += 1
        if wrong_times > 1:
            meaning_entry.config(state="disabled")
            fexam_entry.config(state="disabled")
            feedback_label.config(text="Learn again! ❌", fg="red")
            query = 'update vocabulary set "Start date" = CURRENT_DATE where "Meaning" = %s'
            parameters = (selected_word_data.get("meaning"),)
            run_query(query, parameters)
        else:
            feedback_label.config(text="Wrong!", fg="red")
    def on_word_selected(event):
        global selected_word_data, wrong_times
        wrong_times = 0
        meaning_entry.config(state="normal")
        feedback_label.config(text="")

        try:
            selected_item = tree.selection()[0]
            word = tree.item(selected_item)['values'][0]

            # Fetch full data from the DB
            query = 'SELECT "Meaning", "Example in French","Example in English" FROM vocabulary WHERE "Word" = %s'
            result = run_query(query, (word,))

            if result:
                meaning, example_french, example_english = result[0]
                word_entry.delete(0, END)
                word_entry.insert(0, word)

                eexam_entry.delete(0, END)

                selected_word_data = {
                    "word" : word,
                    "meaning" : meaning,
                    "example_french" : example_french,
                    "example_english" : example_english
                }


        except IndexError:
            pass  # Nothing selected
    def on_meaning_entered(event):
        global wrong_times
        user_meaning = selected_word_data.get("meaning")
        if meaning_entry.get().strip() == user_meaning:
            eexam_entry.delete(0, END)
            eexam_entry.insert(0, selected_word_data.get("example_english"))
            wrong_times = 0
        else:
            check_to_reset()
    def on_fexam_checked():
        global wrong_times, selected_word_data
        user_fexam = selected_word_data.get("example_french")
        if fexam_entry.get() == user_fexam:
            feedback_label.config(text="Correct!", fg="green")
            wrong_times = 0
            query = f'delete from "{day}" where "Meaning" = %s'
            parameters = (selected_word_data.get("meaning"),)
            run_query(query, parameters)
        else:
            check_to_reset()

    # --- Title ---
    title = Label(root, text="📚 Revision", font=("Helvetica", 22, "bold"), bg="#f5f5f5")
    title.pack(pady=20)

    # --- Tree frame ---
    tree_frame = Frame(root)
    tree_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    tree_scroll = Scrollbar(tree_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)

    tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="browse")
    tree.pack(fill=BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_word_selected)
    tree_scroll.config(command=tree.yview)

    tree['columns'] = ("Word",)
    tree.column("#0", width=0, stretch=NO)
    tree.column("Word", anchor=W, width=300)

    tree.heading("Word", text="Word", anchor=W)

    # --- Input Frame ---
    input_frame = LabelFrame(root, text="Enter Word Details", font=("Helvetica", 14),
                             bg="#f5f5f5", bd=2, padx=15, pady=15, labelanchor="n")
    input_frame.pack(pady=10, padx=20, fill="both")

    labels = ["Word", "Meaning", "Example in French", "Example in English"]
    entries = []

    for i, label_text in enumerate(labels):
        row = i // 2
        col = (i % 2) * 2  # 0 or 2

        label = Label(input_frame, text=label_text + ":", font=("Helvetica", 12), bg="#f5f5f5")
        label.grid(row=row, column=col, sticky="w", padx=5, pady=8)

        entry = Entry(input_frame, width=35, font=("Helvetica", 12))
        entry.grid(row=row, column=col + 1, padx=5, pady=8)
        entries.append(entry)

    # --- Unpack entries for easier reference ---
    word_entry, meaning_entry, fexam_entry, eexam_entry= entries
    meaning_entry.bind("<Return>", on_meaning_entered)

    # --- Feedback Label ---
    feedback_label = Label(input_frame, text="", font=("Helvetica", 14, "bold"), bg="#f5f5f5", fg="green")
    feedback_label.grid(row=0, column=4, rowspan=2, padx=20, sticky="n")

    # --- Button ---
    button_frame = Frame(root, bg="#f5f5f5")
    button_frame.pack(pady=10)

    Button(button_frame, text="Check", width=10, bg="#2196F3", fg="white", font=("Helvetica", 11),
           command=on_fexam_checked).grid(row=0, column=0, padx=10)
    Button(button_frame, text="Back", width=10, bg="#9E9E9E", fg="white", font=("Helvetica", 11),
           command=mainMenu).grid(row=0, column=3, padx=10)

    treeview_query = f'SELECT "Word" FROM "{day}" WHERE "Deadline" = CURRENT_DATE;'
    refresh_treeview(tree, treeview_query)

def day_2():
    review_day("Day_2")

def day_4():
    review_day("Day_4")

def day_7():
    review_day("Day_7")

def day_12():
    review_day("Day_12")

def day_21():
    review_day("Day_21")

def run_query(query, parameters=()):
    conn = psycopg2.connect(dbname="learningdb", user="postgres", password="nguyentudtb",
                                host="localhost", port="5432")
    cur = conn.cursor()
    query_result = None
    try:
        cur.execute(query, parameters)
        if query.lower().startswith("select"):
            query_result = cur.fetchall()
        conn.commit()
    except psycopg2.Error as e:
        messagebox.showerror("Database error", str(e))
    finally:
        cur.close()
        conn.close()
    return query_result

# ---Refresh treeview---
def refresh_treeview(tree, query):
    for item in tree.get_children():
        tree.delete(item)

    records = run_query(query)
    for record in records:
        tree.insert('', END, values=record)

mainMenu()

root.mainloop()
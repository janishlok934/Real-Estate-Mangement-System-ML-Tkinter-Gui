import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, os, pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup 
from PIL import Image, ImageTk 
import datetime

DATA_FILE = 'properties.csv'
FAVORITES_FILE = 'favorites_user.csv'
LOGIN_LOG = "login_log.csv"

# Ensure favorites file exists
if not os.path.exists(FAVORITES_FILE):
    with open(FAVORITES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID'])  # Only need to store property IDs


# Load trained ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# Ensure CSV exists with correct headers
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Location', 'Type', 'Price', 'Area', 'Bedrooms', 'Bathrooms', 'Age', 'Image'])
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_HEADER = ("Segoe UI", 16, "bold")
FONT_NORMAL = ("Segoe UI", 11)
FONT_BUTTON = ("Segoe UI", 10, "bold")
BG_COLOR = "#f0f6fc"  # Light bluish background for all panels
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.content = tk.Frame(root, bg=BG_COLOR, bd=2, relief="groove")
        self.root.title("Login - Real Estate Portal")
        self.root.geometry("400x300")

        tk.Label(root, text="🔐 Login", font=("Arial", 20, "bold")).pack(pady=20)

        tk.Label(root, text="Username:", font=("Arial", 12)).pack()
        self.username_entry = tk.Entry(root, font=("Arial", 12))
        self.username_entry.pack(pady=5)

        tk.Label(root, text="Password:", font=("Arial", 12)).pack()
        self.password_entry = tk.Entry(root, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)

        tk.Button(root, text="Login", command=self.login, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        # Ensure login log file exists
        if not os.path.exists(LOGIN_LOG):
            with open(LOGIN_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Username', 'LoginTime'])

        # Inside login() method (after successful login)
        with open(LOGIN_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        # Simple credentials
        credentials = {
            "admin": "admin123",
            "user": "user123"
        }

        if username in credentials and credentials[username] == password:
            self.root.destroy()
            main_root = tk.Tk()
            app = RealEstateApp(main_root, role=username)
            main_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

class RealEstateApp:
    def __init__(self, root, role="user"):
        self.root = root
        self.content = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.role = role
        self.root.title("Real Estate with ML")
        self.root.geometry("1000x650")
        self.root.configure(bg="#f5f7fa")

        # Custom style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#212121",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=FONT_NORMAL)
        style.configure("Treeview.Heading",
                        background="#4CAF50",
                        foreground="white",
                        font=("Segoe UI", 11, "bold"))

        tk.Label(root, text="🏠 Real Estate Portal with Price Prediction", font=FONT_TITLE, bg="#f5f7fa", fg="#37474F").pack(pady=15)

        # Navigation Frame - Row 1
       # Unified Navigation Frame
        nav_frame = tk.Frame(root, bg="#e3eaf0", pady=10)
        nav_frame.pack(fill="x", padx=10)

        # Helper function to make nav buttons
        def make_button(text, cmd, color="#4CAF50"):
            return tk.Button(nav_frame, text=text, command=cmd, font=FONT_BUTTON,
                            bg=color, fg="white", relief="flat", activebackground="#388E3C")

        # Row 1 buttons
        buttons = []

        buttons.append(make_button("📋 View Listings", self.view_properties))
        if self.role == "admin":
            buttons.append(make_button("📋 Admin Dashboard", self.show_admin_dashboard, color="#5C6BC0"))

        if self.role == "admin":
            buttons.append(make_button("➕ Add Property", self.add_property_form))
            buttons.append(make_button("📤 Export", self.export_data))
        buttons.append(make_button("🔍 Search", self.search_property))
        buttons.append(make_button("🆕 Recent", self.show_recent_listings))
        buttons.append(make_button("📊 Price Graph", self.show_price_area_chart))
        buttons.append(make_button("📈 ML Graph View", self.show_ml_graph_view))
        buttons.append(make_button("🌍 Market Trends", self.show_market_trends_offline))
        if self.role == "user":
            buttons.append(make_button("⭐ My Favorites", self.show_favorites))
        buttons.append(make_button("📈 Analytics", self.show_analytics))
        buttons.append(make_button("❌ Exit", root.quit, color="#f44336"))

        # Pack buttons using grid to align properly
        for i, btn in enumerate(buttons):
            btn.grid(row=0, column=i, padx=4, pady=5)

        self.content = tk.Frame(root, bg="#ffffff", bd=2, relief="groove")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)

        self.more_details = {}
        self.selected_image_path = ""
        self.view_properties()


    def show_recent_listings(self):
        self.clear()
        tk.Label(self.content, text="🕒 Recent Listings", font=("Arial", 16)).pack(pady=10)
        tree = ttk.Treeview(self.content, columns=self.columns(), show="headings")
        for col in self.columns():
            tree.heading(col, text=col)
            tree.column(col, width=90)
        with open(DATA_FILE, 'r') as f:
            reader = list(csv.DictReader(f))[-5:]
            for row in reader:
                tree.insert("", tk.END, values=[row.get(col, "") for col in self.columns()])
        tree.pack(fill="both", expand=True)
    def edit_property(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a property to edit.")
            return

        values = tree.item(selected)["values"]
        prop_id = values[0]

        self.clear()
        tk.Label(self.content, text=f"✏️ Edit Property: {prop_id}", font=("Arial", 16), bg=BG_COLOR).pack(pady=10)

        form = tk.Frame(self.content, bg=BG_COLOR)
        form.pack(pady=20)

        fields = ["Title", "Location", "Type", "Price", "Area", "Bedrooms", "Bathrooms", "Age", "Image"]
        entries = {}

        for i, field in enumerate(fields):
            tk.Label(form, text=field, font=("Arial", 12), bg="white").grid(row=i, column=0, sticky="e", pady=3)
            entry = tk.Entry(form, font=("Arial", 12))
            entry.grid(row=i, column=1, padx=10, pady=3)
            entry.insert(0, values[i + 1])
            entries[field] = entry

        def save_edits():
            try:
                new_row = [prop_id] + [entries[field].get().strip() for field in fields]
                updated_rows = []
                with open(DATA_FILE, 'r') as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    for row in reader:
                        if row[0] == prop_id:
                            updated_rows.append(new_row)
                        else:
                            updated_rows.append(row)
                with open(DATA_FILE, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(updated_rows)
                messagebox.showinfo("Updated", "Property updated successfully!")
                self.view_properties()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save edits: {e}")

        tk.Button(form, text="Save Changes", command=save_edits, bg="#4CAF50", fg="white", font=("Arial", 12)).grid(
            row=len(fields), columnspan=2, pady=10)


    def view_properties(self):
        pass  # Stub for the rest of the code you already have

    def add_property_form(self):
        pass

    def search_property(self):
        pass

    def show_price_area_chart(self):
        pass

    def columns(self):
        return ["ID", "Title", "Location", "Type", "Price", "Area", "Bedrooms", "Bathrooms", "Age", "Image"]

    def clear(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def generate_unique_id(self):
        try:
            with open(DATA_FILE, 'r') as f:
                reader = csv.DictReader(f)
                ids = [int(row['ID'][1:]) for row in reader if row['ID'].startswith('P')]
                if ids:
                    return f"P{max(ids)+1}"
        except:
            pass
        return "P1001"
    def delete_property(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a property to delete.")
            return

        values = tree.item(selected)["values"]
        prop_id = values[0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete property {prop_id}?")
        if not confirm:
            return

        try:
            updated_rows = []
            with open(DATA_FILE, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if row[0] != prop_id:
                        updated_rows.append(row)

            with open(DATA_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(updated_rows)

            messagebox.showinfo("Deleted", f"Property {prop_id} deleted successfully.")
            self.view_properties()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete property: {e}")

    def view_properties(self):
        self.clear()
        tk.Label(self.content, text="\U0001F4CB Property Listings", font=("Arial", 16)).pack(pady=10)

        tree_frame = tk.Frame(self.content)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=self.columns(), show="headings", selectmode="browse")
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        for col in self.columns():
            tree.heading(col, text=col)
            tree.column(col, width=90)

        with open(DATA_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tree.insert("", tk.END, values=[row[col] for col in self.columns()])

        def view_selected_image():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a property to view its image.")
                return
            values = tree.item(selected_item)["values"]
            image_path = values[-1]
            if not os.path.exists(image_path):
                messagebox.showerror("Image Error", "Image file not found.")
                return
            img_window = tk.Toplevel(self.root)
            img_window.title("Property Image")
            img = Image.open(image_path).resize((400, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            tk.Label(img_window, image=photo).pack(padx=10, pady=10)
            img_window.image = photo  # hold ref

        tk.Button(self.content, text="🖼️ View Image", command=view_selected_image,
                bg="#795548", fg="white", font=("Arial", 12)).pack(pady=10)

        if self.role == "admin":
            # Admin-only Edit & Delete Buttons
            btn_frame = tk.Frame(self.content, bg="#ffffff")
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="✏️ Edit Property", command=lambda: self.edit_property(tree),
                    bg="#03A9F4", fg="white", font=("Arial", 11)).pack(side="left", padx=5)

            tk.Button(btn_frame, text="🗑️ Delete Property", command=lambda: self.delete_property(tree),
                    bg="#f44336", fg="white", font=("Arial", 11)).pack(side="left", padx=5)

        elif self.role == "user":
            def favorite_selected():
                selected_item = tree.selection()
                if not selected_item:
                    messagebox.showwarning("No Selection", "Select a property to favorite.")
                    return
                property_id = tree.item(selected_item)["values"][0]
                self.toggle_favorite(property_id)

            tk.Button(self.content, text="⭐ Add/Remove Favorite", command=favorite_selected,
                    bg="#FF9800", fg="white", font=("Arial", 12)).pack(pady=10)
    def show_admin_dashboard(self):
        self.clear()
        tk.Label(self.content, text="📋 Admin Dashboard Overview", font=FONT_HEADER, bg=BG_COLOR).pack(pady=10)
        try:
            df = pd.read_csv(DATA_FILE)
            total_listings = len(df)

            # Properties added per day
            added_per_day = {}
            with open(DATA_FILE, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    file_time = os.path.getmtime(DATA_FILE)
                    date_str = datetime.datetime.fromtimestamp(file_time).strftime('%Y-%m-%d')
                    added_per_day[date_str] = added_per_day.get(date_str, 0) + 1

            # Read login logs
            login_df = pd.read_csv(LOGIN_LOG) if os.path.exists(LOGIN_LOG) else pd.DataFrame(columns=["Username", "LoginTime"])
            login_df["LoginTime"] = pd.to_datetime(login_df["LoginTime"], errors='coerce')
            logins_per_day = login_df.groupby(login_df["LoginTime"].dt.date).size()
            most_active_users = login_df["Username"].value_counts().head(3)

            stats = [
                ("🏠 Total Listings", total_listings, "#1E88E5"),
                ("📅 Properties Added Today", added_per_day.get(datetime.date.today().strftime('%Y-%m-%d'), 0), "#43A047"),
                ("👥 Total Logins", len(login_df), "#FB8C00"),
            ]

            for label, value, color in stats:
                frame = tk.Frame(self.content, bg=BG_COLOR)
                frame.pack(fill="x", padx=30, pady=5)
                tk.Label(frame, text=label + ":", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=color).pack(side="left")
                tk.Label(frame, text=value, font=("Segoe UI", 12), bg=BG_COLOR, fg="#37474F").pack(side="left", padx=10)

            # Most Active Users
            tk.Label(self.content, text="🔥 Most Active Users", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg="#8E24AA").pack(pady=(20,5))
            for user, count in most_active_users.items():
                tk.Label(self.content, text=f"{user} — {count} logins", font=("Segoe UI", 11), bg=BG_COLOR, fg="#37474F").pack()

        except Exception as e:
            messagebox.showerror("Dashboard Error", f"Failed to load dashboard:\n{e}")

    def add_property_form(self):
        self.clear()
        tk.Label(self.content, text="➕ Add Property", font=("Arial", 16),bg=BG_COLOR).pack(pady=10)

        form = tk.Frame(self.content, bg=BG_COLOR)
        form.pack(pady=20)

        labels = ['Title', 'Location', 'Type']
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(form, text=label, font=("Arial", 12), bg="white").grid(row=i, column=0, sticky="e", pady=5)
            entry = tk.Entry(form, font=("Arial", 12))
            entry.grid(row=i, column=1, pady=5, padx=10)
            entries[label] = entry

        self.more_details = {"Area": 0, "Bedrooms": 0, "Bathrooms": 0, "Age": 0}

        def open_more_details():
            def save_details():
                try:
                    self.more_details["Area"] = float(area_entry.get())
                    self.more_details["Bedrooms"] = int(bed_entry.get())
                    self.more_details["Bathrooms"] = int(bath_entry.get())
                    self.more_details["Age"] = int(age_entry.get())
                    top.destroy()
                except ValueError:
                    messagebox.showerror("Input Error", "Enter valid numbers.")
            top = tk.Toplevel(self.root)
            top.title("More Property Details")
            tk.Label(top, text="Area (sqft):").grid(row=0, column=0)
            tk.Label(top, text="Bedrooms:").grid(row=1, column=0)
            tk.Label(top, text="Bathrooms:").grid(row=2, column=0)
            tk.Label(top, text="Building Age:").grid(row=3, column=0)

            area_entry = tk.Entry(top)
            bed_entry = tk.Entry(top)
            bath_entry = tk.Entry(top)
            age_entry = tk.Entry(top)
            area_entry.grid(row=0, column=1)
            bed_entry.grid(row=1, column=1)
            bath_entry.grid(row=2, column=1)
            age_entry.grid(row=3, column=1)

            tk.Button(top, text="Save Details", command=save_details).grid(row=4, columnspan=2, pady=10)

        def upload_image():
            file_path = filedialog.askopenfilename(title="Select Property Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
            if file_path:
                self.selected_image_path = file_path
                messagebox.showinfo("Image Selected", "Image path saved.")

        tk.Button(form, text="\U0001F6E0 More Details", command=open_more_details).grid(row=len(labels), columnspan=2, pady=5)
        tk.Button(form, text="\U0001F5BC Upload Image", command=upload_image).grid(row=len(labels)+1, columnspan=2, pady=5)

        def save():
            try:
                uid = self.generate_unique_id()
                data = [entries[label].get().strip() for label in labels]
                if not all(data):
                    raise ValueError("Missing base details")
                area = self.more_details["Area"]
                beds = self.more_details["Bedrooms"]
                baths = self.more_details["Bathrooms"]
                age = self.more_details["Age"]
                X = pd.DataFrame([[area, beds, baths, age]], columns=["Area", "Bedrooms", "Bathrooms", "Age"])
                predicted_price = model.predict(X)[0]
                date_added = datetime.datetime.now().strftime("%Y-%m-%d")
                
                # Create row with all 11 columns in correct order
                row = [
                    uid, 
                    data[0],  # Title
                    data[1],  # Location
                    data[2],  # Type
                    f"{int(predicted_price)}",  # Price
                    str(area),  # Area
                    str(beds),  # Bedrooms
                    str(baths),  # Bathrooms
                    str(age),  # Age
                    self.selected_image_path,  # Image
                    date_added   # Date_Added
                ]
                
                with open(DATA_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
                self.show_loading_screen("Predicting & Saving...", 2000)
                self.root.after(2100, lambda: messagebox.showinfo("Success", f"Property added with predicted price ₹{int(predicted_price)}"))
                self.view_properties()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add property\n{e}")
        tk.Button(form, text="Save Property", command=save, bg="#4CAF50", fg="white", font=("Arial", 12)).grid(row=len(labels)+2, columnspan=2,pady=10)
    def show_ml_graph_view(self):
        try:
            df = pd.read_csv(DATA_FILE)

            if df.empty:
                messagebox.showinfo("No Data", "No property data available to visualize.")
                return

            # Convert required columns to numeric, handling errors
            for col in ["Area", "Bedrooms", "Bathrooms", "Age"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Drop rows with missing values in these columns
            df = df.dropna(subset=["Area", "Bedrooms", "Bathrooms", "Age"])

            if df.empty:
                messagebox.showinfo("No Valid Data", "No property data with valid numeric features.")
                return

            # Prepare features and predictions
            features = df[["Area", "Bedrooms", "Bathrooms", "Age"]]
            predictions = model.predict(features)

            df["Predicted Price"] = predictions

            # Create figure with subplots
            fig, axes = plt.subplots(1, 3, figsize=(18, 5))
            fig.suptitle("ML Predicted Price Comparison (Bar Graphs)", fontsize=16)

            # Plot 1: Predicted Price vs Area
            sorted_df1 = df.sort_values("Area")
            axes[0].bar(sorted_df1["Area"].astype(str), sorted_df1["Predicted Price"], color="skyblue")
            axes[0].set_title("Price vs Area")
            axes[0].set_xlabel("Area (sqft)")
            axes[0].set_ylabel("Predicted Price (₹)")
            axes[0].tick_params(axis='x', rotation=45)

            # Plot 2: Predicted Price vs Bedrooms
            sorted_df2 = df.sort_values("Bedrooms")
            axes[1].bar(sorted_df2["Bedrooms"].astype(str), sorted_df2["Predicted Price"], color="lightgreen")
            axes[1].set_title("Price vs Bedrooms")
            axes[1].set_xlabel("Bedrooms")
            axes[1].set_ylabel("Predicted Price (₹)")
            axes[1].tick_params(axis='x', rotation=45)

            # Plot 3: Predicted Price vs Age
            sorted_df3 = df.sort_values("Age")
            axes[2].bar(sorted_df3["Age"].astype(str), sorted_df3["Predicted Price"], color="salmon")
            axes[2].set_title("Price vs Building Age")
            axes[2].set_xlabel("Age (years)")
            axes[2].set_ylabel("Predicted Price (₹)")
            axes[2].tick_params(axis='x', rotation=45)

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Could not generate ML bar graphs:\n{e}")
    def search_property(self):
        self.clear()
        tk.Label(self.content, text="\U0001F50D Search Property by Location", font=("Arial", 16)).pack(pady=10)
        search_frame = tk.Frame(self.content, bg=BG_COLOR)
        search_frame.pack(pady=20)
        try:
            df = pd.read_csv(DATA_FILE)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read data: {e}")
            return

        locations = sorted(df['Location'].dropna().unique())
        types = sorted(df['Type'].dropna().unique())
        filters = {}

        def add_label_input(text, row, col, entry_width=15):
            tk.Label(search_frame, text=text, font=("Arial", 12), bg=BG_COLOR).grid(row=row, column=col, sticky="e", padx=5, pady=3)
            entry = tk.Entry(search_frame, font=("Arial", 12), width=entry_width)
            entry.grid(row=row, column=col+1, padx=5)
            return entry

        tk.Label(search_frame, text="Location:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="e", padx=5)

        location_var = tk.StringVar()
        loc_entry = tk.Entry(search_frame, textvariable=location_var, font=("Arial", 12), width=17)
        loc_entry.grid(row=0, column=1, padx=5)

        suggestion_box = tk.Listbox(search_frame, height=4, font=("Arial", 11), width=17)
        suggestion_box.grid(row=1, column=1, padx=5, sticky="n")
        suggestion_box.grid_remove()  # Hide initially

        def update_suggestions(event):
            typed = location_var.get().lower()
            suggestion_box.delete(0, tk.END)
            suggestions = [loc for loc in locations if typed in loc.lower()]
            if suggestions:
                for suggestion in suggestions:
                    suggestion_box.insert(tk.END, suggestion)
                suggestion_box.grid()
            else:
                suggestion_box.grid_remove()

        def use_suggestion(event):
            if suggestion_box.curselection():
                selected = suggestion_box.get(suggestion_box.curselection())
                location_var.set(selected)
                suggestion_box.grid_remove()

        loc_entry.bind("<KeyRelease>", update_suggestions)
        suggestion_box.bind("<<ListboxSelect>>", use_suggestion)


        tk.Label(search_frame, text="Type:", font=("Arial", 12), bg=BG_COLOR).grid(row=0, column=2, sticky="e", padx=5)
        type_combo = ttk.Combobox(search_frame, values=types, font=("Arial", 12), width=17)
        type_combo.grid(row=0, column=3, padx=5)

        filters['min_price'] = add_label_input("Min Price (₹):", 1, 0)
        filters['max_price'] = add_label_input("Max Price (₹):", 1, 2)
        filters['min_area'] = add_label_input("Min Area (sqft):", 2, 0)
        filters['max_area'] = add_label_input("Max Area (sqft):", 2, 2)
        filters['min_beds'] = add_label_input("Min Bedrooms:", 3, 0)
        filters['max_beds'] = add_label_input("Max Bedrooms:", 3, 2)

        def do_search():
            try:
                result_frame = tk.Frame(self.content, bg="white")
                result_frame.pack(pady=10, fill="both", expand=True)
                tree = ttk.Treeview(result_frame, columns=self.columns(), show="headings")
                for col in self.columns():
                    tree.heading(col, text=col)
                    tree.column(col, width=90)

                filtered_df = df.copy()
                typed_location = location_var.get().strip()
                if typed_location:
                    if typed_location.lower() not in [loc.lower() for loc in locations]:
                        messagebox.showerror("Invalid Location", f"'{typed_location}' not found in available locations.")
                        return
                    filtered_df = filtered_df[filtered_df['Location'].str.lower() == typed_location.lower()]

                if type_combo.get():
                    filtered_df = filtered_df[filtered_df['Type'].str.lower() == type_combo.get().strip().lower()]

                def get_val(key, cast_type):
                    val = filters[key].get().strip()
                    return cast_type(val) if val else None

                conditions = [
                    ('Price', get_val('min_price', int), '>='),
                    ('Price', get_val('max_price', int), '<='),
                    ('Area', get_val('min_area', float), '>='),
                    ('Area', get_val('max_area', float), '<='),
                    ('Bedrooms', get_val('min_beds', int), '>='),
                    ('Bedrooms', get_val('max_beds', int), '<='),
                ]

                for col, val, op in conditions:
                    if val is not None:
                        if op == '>=':
                            filtered_df = filtered_df[filtered_df[col] >= val]
                        elif op == '<=':
                            filtered_df = filtered_df[filtered_df[col] <= val]

                for _, row in filtered_df.iterrows():
                    tree.insert("", tk.END, values=[row.get(col, "") for col in self.columns()])

                tree.pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {e}")

        tk.Button(search_frame, text="Search", command=do_search, bg="#2196F3", fg="white", font=("Arial", 12)).grid(row=4, columnspan=4, pady=10)

   # Replace your old show_market_trends method with this improved version

    def show_recent_listings(self):
        self.clear()
        tk.Label(self.content, text="\U0001F552 Recent Listings", font=("Arial", 16)).pack(pady=10)
        tree = ttk.Treeview(self.content, columns=self.columns(), show="headings")
        for col in self.columns():
            tree.heading(col, text=col)
            tree.column(col, width=90)
        with open(DATA_FILE, 'r') as f:
            reader = list(csv.DictReader(f))[-1:]
            for row in reader:
                tree.insert("", tk.END, values=[row.get(col, "") for col in self.columns()])
        tree.pack(fill="both", expand=True)

    def show_price_area_chart(self):
        try:
            df = pd.read_csv(DATA_FILE)
            plt.scatter(df['Area'], df['Price'])
            plt.xlabel("Area (sqft)")
            plt.ylabel("Price (₹)")
            plt.title("Price vs Area")
            plt.grid(True)
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Could not show chart: {e}")

    def show_market_trends_offline(self):
        try:
            self.clear()
            tk.Label(self.content, text="🌍 Market Trends (₹/sqft)", font=("Arial", 16)).pack(pady=10)

            # Show loading screen
            self.show_loading_screen("Loading Market Trends...", duration_ms=2000)

            # Delay actual processing slightly so loading bar appears
            self.root.after(2100, self._load_market_trends_graph)

        except Exception as e:
            messagebox.showerror("Error", f"Offline market trend fetch failed:\n{e}")
    def _load_market_trends_graph(self):
        try:
            html_path = os.path.join(os.path.dirname(__file__), "real_estate_market.html")

            with open(html_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            table = soup.find("table", {"id": "trend-table"})
            if not table:
                raise ValueError("No table with id 'trend-table' found in HTML.")

            rows = table.find_all("tr")[1:]  # skip header

            data = []
            for row in rows:
                cols = row.find_all("td")
                location = cols[0].get_text(strip=True)
                price = float(cols[1].get_text(strip=True).replace(",", ""))
                data.append((location, price))

            locations, prices = zip(*data)

            base_colors = [
                "red", "green", "blue", "orange", "purple",
                "teal", "brown", "cyan", "magenta", "gold"
            ]
            if len(locations) > len(base_colors):
                colors = random.choices(base_colors, k=len(locations))
            else:
                colors = base_colors[:len(locations)]

            plt.figure(figsize=(12, 6))
            bars = plt.bar(locations, prices, color=colors)

            plt.title("Market Trends - Price per sqft")
            plt.xlabel("Location")
            plt.ylabel("Price (₹/sqft)")
            plt.xticks(rotation=45)

            for bar, price in zip(bars, prices):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 50,
                        f"₹{int(price)}", ha="center", fontsize=9, fontweight='bold')

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load market trends:\n{e}")


    def show_analytics(self):
        self.clear()
        tk.Label(self.content, text="📊 Property Analytics Dashboard", font=FONT_HEADER, bg=BG_COLOR, fg="#2E7D32").pack(pady=10)

        try:
            df = pd.read_csv(DATA_FILE)

            total_props = len(df)
            avg_price = int(df["Price"].astype(float).mean())
            avg_area = int(df["Area"].astype(float).mean())
            avg_bed = df["Bedrooms"].astype(int).mean()
            avg_bath = df["Bathrooms"].astype(int).mean()
            popular_location = df["Location"].value_counts().idxmax()

            stats = [
                ("🏘️Total Properties", total_props, "#1E88E5"),
                ("💰Avg. Price", f"₹{avg_price:,}", "#43A047"),
                ("📐Avg. Area", f"{avg_area} sqft", "#FB8C00"),
                ("🛏️Avg. Bedrooms", f"{avg_bed:.1f}", "#8E24AA"),
                ("🛁Avg. Bathrooms", f"{avg_bath:.1f}", "#00ACC1"),
                ("📍Most Popular Location", popular_location, "#C62828"),
            ]

            for label, value, color in stats:
                stat_frame = tk.Frame(self.content, bg=BG_COLOR, pady=5)
                stat_frame.pack(fill="x", padx=30)
                tk.Label(stat_frame, text=label + ":", font=("Segoe UI", 12, "bold"), bg=BG_COLOR, fg=color).pack(side="left")
                tk.Label(stat_frame, text=value, font=("Segoe UI", 12), bg=BG_COLOR, fg="#37474F").pack(side="left", padx=10)

        except Exception as e:
            messagebox.showerror("Analytics Error", f"Could not load data: {e}")
    def export_data(self):
        try:
            df = pd.read_csv(DATA_FILE)
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if file_path:
                df.to_csv(file_path, index=False)
                self.show_loading_screen("Exporting data...", 1500)
                self.root.after(1600, lambda: messagebox.showinfo("Exported", f"Data exported to:\n{file_path}"))
        except Exception as e:
            messagebox.showerror("Export Error", f"Export failed: {e}")

    def toggle_favorite(self, property_id):
        if self.role != "user":
            return  # Only users can favorite

        try:
            df = pd.read_csv(FAVORITES_FILE)
            if property_id in df['ID'].values:
                df = df[df['ID'] != property_id]  # remove if already exists
                messagebox.showinfo("Removed", f"Property {property_id} removed from favorites.")
            else:
                df.loc[len(df.index)] = [property_id]
                messagebox.showinfo("Added", f"Property {property_id} added to favorites.")
            df.to_csv(FAVORITES_FILE, index=False)
        except Exception as e:
            messagebox.showerror("Favorite Error", f"Could not update favorites.\n{e}")

    def show_favorites(self):
        self.clear()
        tk.Label(self.content, text="⭐ My Favorites", font=("Arial", 16),bg=BG_COLOR).pack(pady=10)

        try:
            fav_ids = pd.read_csv(FAVORITES_FILE)['ID'].tolist()
            if not fav_ids:
                tk.Label(self.content, text="No favorites yet.", font=("Arial", 12)).pack()
                return

            df = pd.read_csv(DATA_FILE)
            fav_df = df[df['ID'].isin(fav_ids)]

            tree = ttk.Treeview(self.content, columns=self.columns(), show="headings")
            for col in self.columns():
                tree.heading(col, text=col)
                tree.column(col, width=90)

            for _, row in fav_df.iterrows():
                tree.insert("", tk.END, values=[row.get(col, "") for col in self.columns()])
            tree.pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load favorites: {e}")
    def show_loading_screen(self, message="Processing...", duration_ms=2000):
        loading = tk.Toplevel(self.root)
        loading.title("Please wait")
        loading.geometry("300x100")
        loading.resizable(False, False)
        loading.grab_set()
        tk.Label(loading, text=message, font=("Segoe UI", 12)).pack(pady=10)
        progress = ttk.Progressbar(loading, orient="horizontal", length=250, mode="indeterminate")
        progress.pack(pady=10)
        progress.start(10)
        loading.after(duration_ms, lambda: (progress.stop(), loading.destroy()))


if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()
from fasthtml.common import*
from typing import List, Tuple, Optional
from datetime import datetime, time, timedelta
import copy

app, rt = fast_app()
import random

# ฟังก์ชันสำหรับสุ่มสีแบบ Hex
def random_color():
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return f"rgb({r}, {g}, {b})"  # ใช้ RGB ที่สุ่มในช่วงที่เป็นสีอ่อน

class System:
    def __init__(self):
        self.__branches = []
        self.__menu_list = []
        self.__boxset_list = []
        self.__member_list = []
        self.__promotion_list = []
        self.__manager_list = []
        self.__delete_list = []

    def find_delete_food_by_id(self,food_id):
        for menu in self.__delete_list:
            if isinstance(menu,Food):
                if menu.get_food_id() == food_id:
                    return menu
        return None

    def find_delete_boxset_by_id(self,boxset_id):
        for boxset in self.__delete_list:
            if isinstance(boxset,Boxset):
                if boxset.get_boxset_id() == boxset_id:
                    return boxset
        return None

    def add_restore_boxset(self,boxset):
        self.__boxset_list.append(boxset)
        return "SUCCESS"

    def add_restore_food(self,food):
        self.__menu_list.append(food)
        return "SUCCESS"

    def remove_delete_list(self,menu):
        self.__delete_list.remove(menu)
        return "SUCCESS"
    
    def find_type_by_menu_id(self,menu_id):
        
        boxset = self.find_delete_boxset_by_id(menu_id)
        food = self.find_delete_food_by_id(menu_id)
        if boxset:
            return boxset
        
        elif food:
            return food
            
        return None
    

    def restore_item(self, item_id: str, manager: 'Manager'):

        item = self.find_type_by_menu_id(item_id)
        if item:
            if isinstance(item, Food):
                self.add_restore_food(item)
            elif isinstance(item, Boxset):
                self.add_restore_boxset(item)
            else:
                return "INVALID_ITEM"

            self.remove_delete_list(item)
            
            manager.add_manage_history("RESTORE", item_id)
            return Redirect("/restore_delete_menu")
        
        return "ITEM_NOT_FOUND"
    
    def delete_food_menu(self,menu):
        self.__menu_list.remove(menu)

    def delete_boxset_menu(self,boxset):
        self.__boxset_list.remove(boxset)

    def delete_item_by_id(self, item_id: str, item_type: str, manager: 'Manager'):
        if item_type == "food":
            item = self.find_food_by_id(item_id)
            if isinstance(item, Food):
                self.delete_food_menu(item)
                self.add_delete_food_menu(item)
                manager.add_manage_history("DELETE_FOOD", item_id)
                
    
        elif item_type == "boxset":
            item = self.find_boxset_by_id(item_id)
            if isinstance(item, Boxset):
                self.delete_boxset_menu(item)
                self.add_delete_boxset_menu(item)
                manager.add_manage_history("DELETE_BOXSET", item_id)
                

        return Redirect("/delete_menu")
    
                
    def find_free_rider(self,order_type):
        branch = order_type.get_branch()
        rider_in_branch = branch.get_rider()
        for rider in rider_in_branch:

            if rider.check_free() == "FREE":
                rider.set_busy()
                return rider #instance rider
        return "Busy"
        
    def add_admin(self,name,surname,tel_number,email,username,password):
        admin = Manager(name,surname,tel_number,email,username,password)
        self.__manager_list.append(admin)
    
    def add_delete_boxset_menu(self,boxset):
        self.__delete_list.append(boxset)

    def add_delete_food_menu(self,food):
        self.__delete_list.append(food)

    def find_food_by_id(self,food_id):
        for menu in self.__menu_list:
            if isinstance (menu,Food):
                if menu.get_food_id() == food_id:
                    return menu

    def find_boxset_by_id(self,boxset_id):
        for boxset in self.__boxset_list:
             if isinstance (boxset,Boxset):
                if boxset.get_boxset_id() == boxset_id:
                    return boxset
        
    def get_delete_menu(self):
        return self.__delete_list

    def add_member_list(self,account):
        self.__member_list.append(account)

    def get_menu_list(self):
        
        return self.__menu_list
    def create_account(self,name : str ,surname : str ,tel_number : str ,email : str ,username : str ,password : str):
        new_account = Member(name,surname,tel_number,email,username,password)

        self.add_member_list(new_account)
        return "CREATE ACCOUNT SUCCESS"

    def get_member_list(self):
        return self.__member_list
    
    def find_member_by_username(self,username):
        for member in self.__member_list:
            if username == member.get_username():
                return member
        for admin in self.__manager_list:
            if username == admin.get_username():
                return admin
        return "ERROR"
    
    def manage_stock(self,branch):
        member = session.get_current_user()
        basket = member.get_current_basket()
        menu_list = basket.get_item_in_basket()

        for basketitem in menu_list:
            food = basketitem.get_product()
            quantity = basketitem.get_total()
            if isinstance(food,Food):
                branch.reduce_stock(food,quantity)
        
        return "Done"
            
            
    def login(self,username,password):
        member_instance = self.find_member_by_username(username)
        if member_instance == "ERROR":
            return "FAIL"
        login_success = member_instance.verify(password)

        if login_success == "LOGIN SUCCESS":
            return "LOGIN SUCCESS"
        else:
            return "FAIL"
        

    def handle_authentication(self, action, name=None, surname=None, tel_number=None, email=None, username=None, password=None):
        if action == "register":
            result = self.create_account(name, surname, tel_number, email, username, password)
        else:  # action == "login"
            result = self.login(username, password)

        member_instance = self.find_member_by_username(username)

        if (result in ["LOGIN SUCCESS"]):
            session.login(member_instance)
            if (isinstance (member_instance,Member)):
                member_instance.add_basket(Basket())
                return Redirect("/")
        
            elif(isinstance (member_instance,Manager)):
                return Redirect("/manager")
        
        elif result in ["CREATE ACCOUNT SUCCESS"]:
            return Redirect("/")
        else:
            return f"{action.capitalize()} Failed. Try again"

    def add_all_menu_to_branch(self,menu,amount):
        for branch in self.__branches:
            stock = Stock(menu,amount)
            branch.add_stock(stock)
        return "Success"

    def add_food_list(self,food):
        self.__menu_list.append(food)
        return "Success"
    
    def add_food(self, type , name , id , price : int , picture  , amount = 1 ,  select = False ):
        menu = None
        if type == "Savory":
            menu =Savory(name,id,price, picture, select)
        elif type == "Dessert":
            menu = Dessert(name,id,price,picture , select)
        else:
            menu = Drink(name,id,price,picture , select)

        self.add_all_menu_to_branch(menu,amount)
        self.add_food_list(menu)
        return "Success"
        

    def find_menu_by_menu_id(self, menu_list: List[str]):
        menu_instance = []
        for menu in menu_list:
            for food in self.__menu_list:
                if menu == food.get_food_id():
                    menu_instance.append(food)

        return menu_instance

    def add_boxset_list(self, boxset_name: str, boxset_id: str, menu_list: List[str], price: int , picture):
        menu_instance = self.find_menu_by_menu_id(menu_list)
        self.__boxset_list.append(Boxset(boxset_name, boxset_id, menu_instance, price, picture))

    def search_boxset_by_id(self, boxset_id: str):
        for boxset in self.__boxset_list:
            if boxset.get_boxset_id() == boxset_id:
                return boxset
    
    def search_food_by_id(self, food_id : str):
        for food in self.__menu_list:
            if food.get_food_id() == food_id:
                return food
            
    def add_boxselect(self, food_type: str, menu_list: List[str], boxset_id: str ):
        menu_instance = self.find_menu_by_menu_id(menu_list)
        boxselect = BoxSelect(food_type, menu_instance )
        boxset_instance = self.search_boxset_by_id(boxset_id)
        if boxset_instance:
            boxset_instance.add_box_select(boxselect)

    def get_boxset_list(self):
        return self.__boxset_list

    def choose_boxset(self, boxset_id: str, select_list: list , quantity : int):
        boxset_instance = self.search_boxset_by_id(boxset_id)
        
        new_boxset_instance = Boxset(boxset_instance.get_name(),boxset_instance.get_boxset_id(),boxset_instance.get_fixed_menu(),boxset_instance.get_price(),boxset_instance.get_picture())
        new_boxset_instance.add_selected_menu(select_list)
        
        session.get_current_user().get_current_basket().add_basket_item(new_boxset_instance,quantity)
    
    def choose_menu(self,food_id :str , quantity : int , level : str):
        food_instance = self.search_food_by_id(food_id)
        duplicate_food = copy.deepcopy(food_instance)
        if level != None:
            duplicate_food.set_level(level)
        session.get_current_user().get_current_basket().add_basket_item(duplicate_food,quantity)

    def serch_food_instance_by_id(self,food_id):
        for menu in self.__menu_list:
            if menu.get_food_id() == food_id:
                return menu
            
    def add_promotion(self, promotion):
        self.__promotion_list.append(promotion)
    
    def remove_promotion(self, promotion):
        if promotion in self.__promotion_list:
            self.__promotion_list.remove(promotion)
    
    def get_coupon(self, coupon_code):
        for promotion in self.__promotion_list:
            if promotion.verify_coupon(coupon_code):
                print(f"Coupon {coupon_code} found with {promotion.get_discount()*100}% discount")  # Debugging
                return promotion
        print(f"Coupon {coupon_code} not found")  # Debugging
        return None

    def add_pickup_branch(self,branch_info):
        for branch in self.__branches:
            branch_address = branch.get_address()
            branch_district = branch.get_district()

            if branch_address == branch_info['address'] and branch_district == branch_info['district']:
                return branch
        return None
    

    def add_branch(self,zip,district,province):

        branch = Branch(zip,district,province)
        self.__branches.append(branch)

    def find_branch_from_post(self, post_number: str):
        try:
            post_number = int(post_number)
        except ValueError:
            return [] 

        matched_branches = [branch.get_branch_info() for branch in self.__branches if branch.get_branch_info()['postcode'] == post_number]
        return matched_branches

    def search_branches(self, postcode: str):
        branch_list = self.find_branch_from_post(postcode)
        if branch_list:
            return Div(
                *[
                    Div(
                        Div(
                            H3(f"สาขา : {branch['district']}", cls="branch-title"),
                            P(f"ที่อยู่ : {branch['address']}", cls="branch-address"),
                            Button("เลือก",
                                   hx_post="/select_branch",
                                   hx_vals={  # เพิ่ม postcode
                                        "district": branch["district"], 
                                        "address": branch["address"],
                                        "postcode" : postcode
                                        },
                                   hx_target="#selected_branch",
                                   cls="select-button"
                            )
                        ),
                        cls="branch-card"
                    )
                    for branch in branch_list
                ]
            )
        else:
            return B("ไม่พบสาขาสำหรับรหัสไปรษณีย์นี้", cls="no-branch")
    
    def add_rider(self,name,surname,tel_number,email,postcode):
        rider = Rider(name,surname,tel_number,email,postcode)
        for branch in self.__branches:
            if branch.get_postcode() == postcode:
                branch.add_rider(rider)
                return "ADD RIDER SUCCESS"

    def get_stock_by_food_name(self, name):
        for stock in self.__stock:
            if(stock.get_product.get_name == name):
                return stock

    def get_delete_menu(self):
        return self.__delete_list
    
    def create_member(self, name, surname, account_ID, tel_no, address, email, username, password):
        new_member = Member(name, surname, account_ID, tel_no, address, email, username, password, Basket())
        self.__member_list.append(new_member)
        return new_member

    def get_coupon(self, coupon_code):
        for promotion in self.__promotion_list:
            if promotion.verify_coupon(coupon_code):
                return promotion
        return None

    def summary_order(self):

        member = session.get_current_user()
        if not member:
            return None
        return member.summary_order()  # ส่ง system เข้าไปด้วย
    
    def find_near_branch(self, address):
        for branch in self.__branches:
            postcode = str(branch.get_postcode())  # แปลง postcode เป็น string
            if postcode in address:
                return branch
            
        return None
    
    def find_branch_by_post_code(self,postcode):
        for branch in self.__branches:
            if branch.get_postcode() == postcode:
                return branch

class OrderHistory:
    __current_order_id = 67010000

    def __init__(self, member_id , order_type , basket, rider = None ):
        self.__member = member_id
        self.__order_ID = OrderHistory.__current_order_id
        OrderHistory.__current_order_id += 1  
        self.__order_type = order_type 
        self.__basket = basket
        self.__rider = rider
        
    def get_order_id(self):
        return self.__order_ID

    def get_order_type(self):
        return self.__order_type
    
class Account:
    __current_member_id = 1000000
    def __init__(self,name,surname,tel_number,email):
        self.__name = name
        self.__surname = surname
        self.__tel_number = tel_number
        self.__email = email
        self.__account_id = Account.__current_member_id
        Account.__current_member_id += 1

    def get_account_name(self):
        return self.__name
    
    def get_account_surname(self):
        return self.__surname
    
    def get_email(self):
        return self.__email
    
    def get_account_id(self):
        return self.__account_id

    def get_member_info(self):
        return [self.__name, self.__surname, self.__account_id, self.__tel_number, self.__email] 

    @property
    def get_id(self):
        return self.__account_id
    
class Delivery:
    def __init__(self):
        self.__address = None
        self.__branch = None

    def get_address(self):
        return self.__address
    
    def set_address(self, address_info: str):
        self.__address = address_info
        branch = system.find_near_branch(address_info)
        self.set_branch(branch)   
        
        return "Done"

    def set_branch(self,branch : 'Branch'): #instance branch
        self.__branch = branch

    def get_branch(self):
        return self.__branch
    
class PickUp:
    def __init__(self):
        self.__selected_branch = None
        self.__branch = None

    def get_selected_branch(self):
        return self.__selected_branch

    def set_branch(self, branch_info):
        self.__selected_branch = branch_info
        self.select_branch()
        return "Done"

    def select_branch(self):
        branch = system.add_pickup_branch(self.__selected_branch)
        self.__branch = branch
        return "Done"

    def get_branch(self):
        return self.__branch



class Branch:
    def __init__(self, postcode, district, address):
        self.__postcode = postcode
        self.__district = district
        self.__address = address
        self.__rider_list = []
        self.__stock_list = []
    def get_branch_info(self):
        return {
            "postcode": self.__postcode,  
            "district": self.__district,  
            "address": self.__address
        }
    
    def get_address(self):
        return self.__address
    
    def get_district(self):
        return self.__district
    def add_rider(self,rider):
        self.__rider_list.append(rider)        
    
    def get_postcode(self):
        return self.__postcode
    
    def get_rider(self):
        return self.__rider_list
    
    def get_branch_address(self):
        return f"สาขา: {self.__postcode} เขต: {self.__district} จังหวัด: {self.__address}"
    
    def add_stock(self,stock):
        self.__stock_list.append(stock)
        return "Success"

    def reduce_stock(self,food,quantity : int):
        
        stock = self.find_stock_by_food(food)

        result = stock.reduce_quantity(quantity)
        if result:
            return "Success"
        
        return None
    
    def find_stock_by_food(self,food):
        for stock in self.__stock_list:
            if stock.get_food().get_food_id() == food.get_food_id():
                return stock
            
        return None
class Manager(Account):
    def __init__(self, name, surname, tel_number, email,username,password):
        super().__init__(name, surname, tel_number, email)
        self.manage_history = []
        self.__username = username
        self.__password = password

    def add_manage_history(self,type,menu_id):
        self.manage_history.append(f"{type} : {menu_id}")

    def get_username(self):
        return self.__username

    def verify(self, password):
        if self.__password == password:
            return "LOGIN SUCCESS"
        else:
            return "LOGIN FAIL"
        
    def get_username(self):
        return self.__username


class Member(Account):
    def __init__(self, name, surname, tel_number, email,username,password):
        super().__init__(name, surname, tel_number, email)
        self.__username = username
        self.__password = password
        self.__current_basket = None
        self.__order_type = None
        self.__order_history = []

    def add_order_history(self,order,Order):
        self.__order_history.append(order)

    def get_order_type(self):
        return self.__order_type
    
    def add_order_type(self,order):
        self.__order_type = order

    def get_username(self):
        return self.__username
    
    def add_delivery(self,delivery):
        self.__delivery = delivery

    def make_new_order(self):
        self.__current_basket = Basket()
        self.__order_type = None

    def change_password(self, old_password, new_password):
        if old_password == self.__password:
            self.__password = new_password
            return "Password changed successfully!"
        else:
            return "Old password is incorrect."

    def verify(self, password):
        if self.__password == password:
            return "LOGIN SUCCESS"
        else:
            return "LOGIN FAIL"

    def add_basket(self,basket):
        self.__current_basket = basket
    
    def get_current_basket(self):
        return self.__current_basket
    
    def view_basket(self, coupon_code=""):
        return self.__current_basket.item_selected(coupon_code)
    
    def summary_order(self):
        user_info = self.get_member_info()
        
        items, total_price, discount_applied, discount_include = self.__current_basket.item_selected()
        order_type = self.__order_type
        return [user_info, items, total_price, order_type, discount_applied]
    
    def create_order_history(self,rider = None):
        order_history = OrderHistory(self.get_account_id(), self.__order_type, self.__current_basket,rider)
        self.add_order_history(order_history)
        return order_history
    
    def add_order_history(self,order):
        self.__order_history.append(order)
        return "Done"
    
    def reset_basket(self):
        self.__current_basket = Basket()
    
    def get_order_history(self):
        return self.__order_history
class PickedItem:
    def __init__(self, product, quantity: int):
        self.__product = product  
        self.__quantity = quantity

    def get_item_info(self):
        
        return {
            
            "name": self.__product,
            "quantity": self.__quantity
        }   

    def get_product(self):
        return self.__product

    def get_total(self):
        return self.__quantity
    
    def increase_quantity(self, total: int):
        self.__quantity += total


class Basket:
    def __init__(self):
        self.__items = []
    
    def get_item_in_basket(self):
        return self.__items
    

    def check_empty(self):
        return bool(self.__items)  # คืนค่า True ถ้ามีสินค้าอยู่ในตะกร้า
    
    def check_exist(self, item):

        if isinstance(item,Boxset):
            for pickedbasket in self.__items:
                boxset = pickedbasket.get_product()
                if isinstance(boxset, Boxset):
                    if (item.get_boxset_id() == boxset.get_boxset_id()) and (item.get_selected_menu() == boxset.get_selected_menu()):
                        return pickedbasket  # ✅ คืน PickedItem เดิม ถ้าพบ
        elif isinstance(item,Food):
            for pickedbasket in self.__items:
                food = pickedbasket.get_product()
                if isinstance(food,Food):
                    if (item.get_food_id() == food.get_food_id()) and (item.get_select() == food.get_select()):
                        return pickedbasket

        return None

    
    def add_basket_item(self, item, quantity: int):
        pickeditem = PickedItem(item, quantity)

        if (isinstance(item,Boxset)) or (isinstance(item,Food)):
            check_exist = self.check_exist(item)

            if isinstance (check_exist,PickedItem):
                check_exist.increase_quantity(quantity)  # เพิ่มจำนวนถ้ามีอยู่แล้ว
                return "Done"

            self.__items.append(pickeditem)
            return "Done"

        
    def remove_basket_item(self, item_name):
        self.__items = [item for item in self.__items if item.get_item_info()["name"] != item_name]

    def calculate_total_price(self):
        total_price = 0
        for pickeditem in self.__items:
            product = pickeditem.get_product()
            total_price += int(int(product.get_price()) *int( pickeditem.get_total()))

        return total_price

    def item_selected(self, coupon_code=""):
        items = [item.get_item_info() for item in self.__items]
        total_price = self.calculate_total_price()
        discount_applied = 0
        discount_include = total_price  # ตั้งค่าให้เริ่มต้นเป็นราคาปกติ

        if coupon_code:
            promotion = system.get_coupon(coupon_code)
            if promotion:
                discount_applied = total_price * promotion.get_discount()
                discount_include = total_price - discount_applied  # ราคาหลังลด

        return items, total_price, discount_applied, discount_include

class Food:
    def __init__(self, food_name: str, food_id: str, price: int , picture ):
        self.__food_name = food_name
        self.__food_id = food_id
        self.__food_price = price
        self.__food_picture = picture
        self.__status = "AVAILABLE"

    def change_status(self):
        self.__status = None

    def check_status(self):
        return self.__status
    
    def get_name(self):
        return self.__food_name

    def get_food_id(self):
        return self.__food_id

    def get_price(self):
        return self.__food_price

    def get_id(self):
        return self.__food_id
    
    def get_picture(self):
        return self.__food_picture
    
class Savory(Food):
    def __init__(self, food_name, food_id, price , picture, spicy_level = None ):
        super().__init__(food_name, food_id, price, picture)
        self.__spicy_level = spicy_level

    def get_select(self):
        return self.__spicy_level

    def set_level(self,level):
        self.__spicy_level = level

class Dessert(Food):
    def __init__(self, food_name, food_id, price , picture, type = None):
        super().__init__(food_name, food_id, price,picture)
        self.__sugar_free = type

    def get_select(self):
        return self.__sugar_free
    
class Drink(Food):
    def __init__(self, food_name, food_id, price , picture , sweet_level = None):
        super().__init__(food_name, food_id, price , picture)
        self.__sweet_level = sweet_level
    
    def get_select(self):
        return self.__sweet_level

    def set_level(self,level):
        self.__sweet_level = level

class Stock:
    def __init__(self, food_instance: Food, amount: int):
        self.__food = food_instance
        self.__amount = amount

    def reduce_amount(self, total: int):
        self.__amount -= total

    def get_food(self):
        return self.__food

    def add_stock(self,total : int):
        self.__amount += total

    def get_total_amount(self):
        return self.__amount
    
    def reduce_quantity(self, quantity : int):
        total = self.__amount - int(quantity)
        if total >= 0:
            self.__amount = total
            return "Done"
        
        return None
class Boxset:
    def __init__(self, name: str, boxset_id: str, menu: List[Food], price: int, picture):
        self.__boxset_name = name
        self.__boxset_id = boxset_id
        self.__fixed_menu = menu
        self.__price = price
        self.__boxselect = []
        self.__selected_menu = []
        self.__picture = picture

    def get_boxset_id(self):
        return self.__boxset_id

    def add_box_select(self, box_select):
        self.__boxselect.append(box_select)

    def get_name(self):
        return self.__boxset_name

    def get_fixed_menu(self):
        return self.__fixed_menu

    def get_box_select_list(self):
        return self.__boxselect

    def get_price(self):
        return self.__price
    
    def add_selected_menu(self,selected_menu : list):
        for menu in selected_menu:
            self.__selected_menu.append(menu)

    def get_selected_menu(self):
        return self.__selected_menu
    

    def get_picture(self):
        return self.__picture
    
class BoxSelect:
    def __init__(self, menu_type: str, select_option: List[Food] ):
        self.__menu_type = menu_type
        self.__select_option = select_option
        
        

    def select_good_in_set(self, selected: Food):
        if selected in self.__select_option:
            self.__selected_menu = selected

    def get_menu_type(self):
        return self.__menu_type

    def get_select_option(self):
        return self.__select_option

    
    
    def get_select_option_id(self):
        return [id.get_food_id() for id in self.__select_option]

    
class Promotion:
    def __init__(self, coupon_code, discount):
        self.__coupon_code = coupon_code
        self.__discount = discount
    
    def verify_coupon(self, coupon_code):
        return self.__coupon_code == coupon_code
    
    def get_discount(self):
        return self.__discount

class SessionManager:
    def __init__(self):
        self.current_user = None 
    
    def login(self, username):
        self.current_user = username  

    def logout(self):
        self.current_user = None 

    def get_current_user(self):
        return self.current_user

class Rider(Account):
    def __init__(self, name, surname, tel_number, email,branch):
        super().__init__(name, surname, tel_number, email)
        self.__branch = branch
        self.__work_status = "FREE"
        self.__delivery_history = []
    
    def add_delivery_history(self,delivert_history):
        self.__delivery_history.append(delivert_history)

    def check_free(self):
        if self.__work_status == "FREE":
            return "FREE"
        return "BUSY"
    
    def set_free(self):
        self.__work_status = "FREE"
    
    def set_busy(self):
        self.__work_status = "BUSY"

    def get_branch(self):
        return self.__branch
    
    def get_branch_info(self):
        return self.__branch.get_branch_address()
session = SessionManager()        
system = System()
member = system.create_account("sky","sinthaveelert","0613153416","badinskysky@gmail.com","skyzaza","1234")
manager = system.add_admin("Sky","Sinthaveelert","0613153416","badinskysky@gmail.com","sky","1234")
system.add_branch("10200", "พระนคร", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10300", "ดุสิต", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10530", "หนองจอก", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10500", "บางรัก", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10220", "บางเขน", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10240", "บางกะปิ", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10330", "ปทุมวัน", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10100", "ป้อมปราบศัตรูพ่าย", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10260", "พระโขนง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10510, "มีนบุรี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10520, "ลาดกระบัง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "ยานนาวา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10100, "สัมพันธวงศ์", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "พญาไท", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "ธนบุรี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "บางกอกใหญ่", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10310, "ห้วยขวาง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "คลองสาน", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10170, "ตลิ่งชัน", "กรุงเทพ, ประเทศไทย"),
system.add_branch(10700, "บางกอกน้อย", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "บางขุนเทียน", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10160, "ภาษีเจริญ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10140, "ราษฎร์บูรณะ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10700, "บางพลัด", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "ดินแดง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "บึงกุ่ม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "สาทร", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10800, "บางซื่อ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10900, "จตุจักร", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "บางคอแหลม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10250, "ประเวศ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10110, "คลองเตย", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10250, "สวนหลวง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "จอมทอง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10210, "ดอนเมือง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "ราชเทวี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10230, "ลาดพร้าว", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10110, "วัฒนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "สะพานสูง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10100, "สัมพันธวงศ์", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10220, "สายไหม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10230, "คันนายาว", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "สะพานสูง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10310, "วังทองหลาง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10510, "คลองสามวา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10260, "บางนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10170, "ทวีวัฒนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10140, "ทุ่งครุ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "บางบอน", "กรุงเทพ,ประเทศไทย")

branches = [
    (10200, "พระนคร"), (10300, "ดุสิต"), (10530, "หนองจอก"), (10500, "บางรัก"),
    (10220, "บางเขน"), (10240, "บางกะปิ"), (10330, "ปทุมวัน"), (10100, "ป้อมปราบศัตรูพ่าย"),
    (10260, "พระโขนง"), (10510, "มีนบุรี"), (10520, "ลาดกระบัง"), (10120, "ยานนาวา"),
    (10100, "สัมพันธวงศ์"), (10400, "พญาไท"), (10600, "ธนบุรี"), (10600, "บางกอกใหญ่"),
    (10310, "ห้วยขวาง"), (10600, "คลองสาน"), (10170, "ตลิ่งชัน"), (10700, "บางกอกน้อย"),
    (10150, "บางขุนเทียน"), (10160, "ภาษีเจริญ"), (10140, "ราษฎร์บูรณะ"), (10700, "บางพลัด"),
    (10400, "ดินแดง"), (10240, "บึงกุ่ม"), (10120, "สาทร"), (10800, "บางซื่อ"),
    (10900, "จตุจักร"), (10120, "บางคอแหลม"), (10250, "ประเวศ"), (10110, "คลองเตย"),
    (10250, "สวนหลวง"), (10150, "จอมทอง"), (10210, "ดอนเมือง"), (10400, "ราชเทวี"),
    (10230, "ลาดพร้าว"), (10110, "วัฒนา"), (10240, "สะพานสูง"), (10100, "สัมพันธวงศ์"),
    (10220, "สายไหม"), (10230, "คันนายาว"), (10240, "สะพานสูง"),
    (10310, "วังทองหลาง"), (10510, "คลองสามวา"), (10260, "บางนา"), (10170, "ทวีวัฒนา"),
    (10140, "ทุ่งครุ"), (10150, "บางบอน")
]

# Create two riders for each branch with post code only
for branch_code, branch_name in branches:
    # Create two riders for each branch
    rider1 = system.add_rider("Rider1","ABC", "1234567890", "rider1@ABC.com",branch_code)
    rider2 = system.add_rider("Rider2", "EFG", "0987654321","rider2@EFG.com",branch_code)



system.add_food("Savory", "ไก่ทอดสูตรผู้พันโดม","10001",39 , "https://images.ctfassets.net/n4pc9wlortyn/1PTqNXLJLaeEmb1OB3Crgr/772c24e56b996d1c8894d355a6dca910/1_pc._Fried_Chicken_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "ไก่วิงซ์แซ่บ 2 ชิ้น","10002",75 , "https://images.ctfassets.net/n4pc9wlortyn/5NMycxbXDszGSlDBQ0LEEW/18470f88d6aeca847329d2ccc2de7940/2_pcs._WingZ_Zabb_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "ไก่ไม่มีกระดูก 2 ชิ้น", "10003" , 75 , "https://images.ctfassets.net/n4pc9wlortyn/1lUP8d7TNIwllDocIHuy7o/d4b6b241aec6fc8f9074bf982d0853a5/2_pcs._Crispy_Strip_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "นักเก็ตส์  7 ชิ้น" , "10004" , 50 , "https://images.ctfassets.net/n4pc9wlortyn/ixqPr5roRfvh88mGjAQi8/3b2fb1630828999a6045d7309ac0df9a/7_pcs._Chicken_Pop_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "กุ้งโดนัท 1 ชิ้น" , "10005" , 55 , "https://images.ctfassets.net/n4pc9wlortyn/6QPqFn9J7F68ubgbb16u1j/e4463b4b52808563fbd688224857645d/Shrimp_Donut_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "ทาร์ตไข่ 1 ชิ้น" , "10006", 35 , "https://images.ctfassets.net/n4pc9wlortyn/6eueZZxvmoj0TyEDoiHT2K/342d84453f0f7bab4481cb82cde0e1d3/1_pc._Egg_Tart_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "ข้าวไก่กรอบ" , "10007" , 60 ,"https://images.ctfassets.net/n4pc9wlortyn/5CHcoRrT9cSHrtQfYQXZst/e3c61128536a29d7c5a80cded0aee179/Spicy_Chicken_Rice_Bowl_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100,select=True)
system.add_food("Savory" , "ข้าวแกงเขียวหวานไก่" , "10008", 89 , "https://images.ctfassets.net/n4pc9wlortyn/5ibn1iVcubtz7LLDwedId9/c04976ee0489aea0c76468fb7b55497a/Green_Curry_Rice_Bowl_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100,select=True)
system.add_food("Savory" , "ข้าวหอมมะลิ" , "10009" , 35 , "https://images.ctfassets.net/n4pc9wlortyn/OXZHelDGLBtXt6nux2TkH/8a1c60461d1010ac1489ca608b48dad1/Plain_Rice_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100)

system.add_food("Dessert" , "Solf Serve" , "11000", 19 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558434037.png", amount = 100)
system.add_food("Dessert" , "Donut Spinkle" , "11001" , 35 , "http://www.misterdonut.co.th/upload_file/menu/170420101412_02-Suger-Raise-big.png", amount = 100)
system.add_food("Dessert" , "Chocolate Sunday" , "11002" , 35 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558601385.png", amount = 100)
system.add_food("Dessert" , "Strawberry Sunday" , "11003" , 35 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558601312.png" , amount = 100) 

system.add_food("Drink" , "Pepsi" , "12000" , 20 , "https://images.ctfassets.net/n4pc9wlortyn/6vvUyuXaRROoCVhOY3nmLX/a248ffc9305534fbdedb16e695ee3892/Pepsi_1_Glass_480x388.png?h=600&w=800&fm=webp&fit=fill" , amount = 100)
system.add_food("Drink" , "Mineral Water" , "12001" , 15 , "https://images.ctfassets.net/n4pc9wlortyn/4l7HHuczM6P3Y2gL6F5282/3b7876ba9331342253b1d4a2ebe22491/Mineral_Water_480x388.png?h=600&w=800&fm=webp&fit=fill" ,amount = 100)
system.add_food("Drink" , "Drink-7" , "12002" , 20 , "https://images.ctfassets.net/n4pc9wlortyn/gyIOI9C9CoZNqdzKh2CYQ/ff975f64f6334b2882837c4c746aea02/7-Up_No_Sugar_480x388.png?h=600&w=800&fm=webp&fit=fill")
system.add_food("Drink" , "Matcha" , "12003", 35 ,"https://images.ctfassets.net/n4pc9wlortyn/2faQl2VCe9TYtYL0JINtWR/e9fe656929dd3b1c806b713c1c55e8bd/Iced_Matcha_Latte_16oz_480x388.png?h=600&w=800&fm=webp&fit=fill" , amount = 100  ,select=True)
system.add_food("Drink" , "Espresso" , "12004" , 35,"https://images.ctfassets.net/n4pc9wlortyn/SmlGNIBr0mCxoeCtrm9vS/9bf614db87a44eeb7036ad0ae667c269/IcedEspresso_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True )
system.add_food("Drink" , "Chocolate" , "12005" , 40 ,"https://images.ctfassets.net/n4pc9wlortyn/5gEPCPZ82XxSb36U7brrfP/52ea873bd8e41d5c9a19336a0efdff85/IcedChocolate_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True )
system.add_food("Drink" , "Pink Milk" , "12006", 40 ,"https://images.ctfassets.net/n4pc9wlortyn/7BEkkFswnPpISyARO0zOc2/da0218514b5079ee9368d4cdd1aea38c/IcedPinkyMilk_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True)

system.add_boxset_list("ชุดอิ่มแน่นอน", "1001", ["10001", "10006"], 500, "https://images.ctfassets.net/n4pc9wlortyn/7MQe9UhiKuB8gLMXorUorW/f0173ffc64c4b12ea3c11831634359df/Party-Buldak-wingz.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดสุดคุ้ม", "1002", ["10008", "12002"], 100,"https://images.ctfassets.net/n4pc9wlortyn/7BoZpkNiyICqN9CLgBl9J8/3806c7658e37067c0e395eae8b31cf3b/JPU_The_Box_Signature_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดไก่เลิฟเวอร์", "1003", ["10002", "10001"], 50, "https://images.ctfassets.net/n4pc9wlortyn/1VynJvkHfHS2QFjNLvvjYS/a61598f75cae5c805d255180d4b12746/JPU_The_Box_All_Rice_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดเครื่องเคียง", "1004", ["10005", "10006"], 180, "https://images.ctfassets.net/n4pc9wlortyn/561btRzoDxiDE4atf9Miih/2a4833d320c9938f5323a7d74c203ac7/JPU_Im_Suk_Jai_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดอิ่มไหม", "1005", ["10007", "10005"], 50, "https://images.ctfassets.net/n4pc9wlortyn/3J3gMlQgk3yI9LxUD2YqGn/2ea86690e0a84f03e7f3afb2899664c4/The-box-Buldak-wingz.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดไก่กรอบอร่อย", "1006", ["10002", "11003"], 100, "https://images.ctfassets.net/n4pc9wlortyn/6xIGgEQ7eJdaKdTRSUGajq/6d5552112fa3f6fbdbbc86890f355309/JPU_Zinger_Set_480x388.png?h=900&w=1200&fm=webp&fit=fill")

system.add_boxselect("เครื่องดื่มโดนใจ", ["12000", "12001","12002"], "1001")
system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1001")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1002")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006"], "1002")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1003")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003","11001"], "1004")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006","10004"], "1004")
system.add_boxselect("ข้าวเซ็ตโดนใจ", ["10009", "10008"], "1004")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003","11001"], "1005")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006","10004"], "1005")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1006")

system.add_promotion(Promotion("DISCOUNT10", 0.10))  # ส่วนลด 10%
system.add_promotion(Promotion("DISCOUNT20", 0.20))  # ส่วนลด 20%


def navbar():
    if session.get_current_user():  # Check if the current user is logged in
        user = Div(
            Button("CART", onclick="window.location.href='/basket';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            Button("LOGOUT", onclick="window.location.href='/logout';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
            "margin-left": "auto"
            }
        )
    else:
        user = Div(
            Button("CART", onclick="window.location.href='/basket';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
            Button("LOGIN", onclick="window.location.href='/login';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
            Button("Sign In", onclick="window.location.href='/register';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
                "margin-left": "auto"
        }
        )


    return Div(
        Button("OUR SERVICE", onclick="window.location.href='/';",style={
            "font-weight" : "700",
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "36px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("Menu",onclick="window.location.href='/menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        user,
        style={
            "background-color" : "white",
            "display": "flex",
            "align-items": "center",
            "width": "100%"
        }
    )

def managebar():
    user = Div(
            
            Button("LOGOUT", onclick="window.location.href='/logout';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
            "margin-left": "auto"
            }
        )
    
    return Div(
        Button("OUR SERVICE", onclick="window.location.href='/manager';",style={
            "font-weight" : "700",
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "36px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("MenageMenu",onclick="window.location.href='/manage_menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("RestoreMenu",onclick="window.location.href='/restore_delete_menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("MenuDetail",onclick="window.location.href='/menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        user,
        style={
            "background-color" : "white",
            "display": "flex",
            "align-items": "center",
            "width": "100%"
        }
    )

def order_section():
    member = session.get_current_user()
    if isinstance(member,Manager):
        return Div(
            H5("WELCOME MANAGER", style={
                "color": "white",
                "margin-top": "20px",
                "text-align": "center",  # จัดกลางข้อความ
            }),
            style={
                "background-color": "black",
                "color": "white",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "height": "10vh",
                "width": "100%",  # เปลี่ยนจาก 100vw เป็น 100% ป้องกันล้น
                "max-width": "100vw",  # จำกัดไม่ให้เกินจอ
                "margin": "0 auto",  # จัดให้อยู่ตรงกลาง
                "padding": "0",
                "box-sizing": "border-box",
                "overflow-x": "hidden",
            }
        )
    order_type = member.get_order_type() if member else None

    # กรณีที่ยังไม่ได้เลือกประเภทการสั่งซื้อ
    if not order_type:
        return Div(
            H5("LET'S ORDER FOR PICK UP OR DELIVERY", style={
                "color": "white",
                "margin-top": "20px",
                "text-align": "center",  # จัดกลางข้อความ
            }),
            Button("Start Order", onclick="window.location.href='/selectdelivery';", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
            style={
                "background-color": "black",
                "color": "white",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "height": "10vh",
                "width": "100%",  # เปลี่ยนจาก 100vw เป็น 100% ป้องกันล้น
                "max-width": "100vw",  # จำกัดไม่ให้เกินจอ
                "margin": "0 auto",  # จัดให้อยู่ตรงกลาง
                "padding": "0",
                "box-sizing": "border-box",
                "overflow-x": "hidden",
            }
        )
    
    # ถ้ามีการเลือกประเภทการสั่งซื้อแล้ว
    order_type_text = H2("Order Type : Delivery", style={"color": "white", "margin-top" : "15px"}) if isinstance(order_type, Delivery) else H2("Order Type : PICK UP", style={"color": "white", "margin-top" : "15px"})

    # สร้าง Div ที่แสดงประเภทการสั่งซื้อและปุ่ม Change
    return Div(
        order_type_text,
        Button("CHANGE", onclick="window.location.href='/selectdelivery';", style={
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "24px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    )
@rt("/logout")
def logout():
    session.logout()
    return Redirect("/")

@rt("/boxset/{boxset_id}")
def boxset_detail(boxset_id: str):
    boxset = system.search_boxset_by_id(boxset_id)
    if not boxset:
        return P("Boxset not found.")
    
    boxset_name = boxset.get_name()
    container_content = [
        navbar(),       # เรียกใช้ Navbar
        order_section(),# เรียกใช้ Order Section
    ]
    
    # --- Top Section: แสดงภาพและ counter (สำหรับการแสดงผลเท่านั้น) ---
    top_section = Div(
        # ด้านซ้าย: แสดงภาพ
        Div(
            Img(
                src=boxset.get_picture(),  
                style={
                    "width": "30vw",      
                    "height": "50vh", 
                    "object-fit": "cover",
                    "border-radius": "8px",
                    "margin": "30px",
                }
            ),
            style={"flex": "1", "text-align": "center"}
        ),
        # ด้านขวา: แสดงชื่อเซต, ราคา (ถ้ามี) และ counter
        Div(
            Div(
                H1(boxset_name, style={"margin-bottom": "20px"}),
                # (ถ้ามีข้อมูลราคา สามารถเพิ่ม P สำหรับราคาได้ที่นี่)
                Button("+", onclick="updateCounter('increase')", style={
                    "background": "#4CAF50", 
                    "border": "none", 
                    "color": "white", 
                    "font-size": "24px", 
                    "cursor": "pointer", 
                    "padding": "10px 20px",
                    "border-radius": "20px",
                    "box-shadow": "0 4px 6px rgba(0,0,0,0.3)"
                }),
                Span(id="counter", style={
                    "margin": "0 20px", 
                    "font-size": "24px", 
                    "font-weight": "bold"
                }),
                Button("-", onclick="updateCounter('decrease')", style={
                    "background": "#f44336", 
                    "border": "none", 
                    "color": "white", 
                    "font-size": "24px", 
                    "cursor": "pointer", 
                    "padding": "10px 20px",
                    "border-radius": "20px",
                    "box-shadow": "0 4px 6px rgba(0,0,0,0.3)"
                }),
                style={
                    "text-align": "center", 
                    "margin-bottom": "10px",
                    "background": "white",
                    "height": "40vh",
                    "width": "40vw",
                    "border-radius": "10px",
                    "box-shadow": "0 4px 10px rgba(0,0,0,0.2)",
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "center",
                    "align-items": "center"
                }
            ),
            style={
                "flex": "1", 
                "text-align": "center",
                "display": "flex", 
                "flex-direction": "column", 
                "align-items": "center"
            }
        ),
        style={
            "background-color": "#f2f1ec",
            "display": "flex", 
            "width": "100%", 
            "justify-content": "space-around", 
            "align-items": "center",
            "padding": "20px",
            "box-sizing": "border-box",
            "border-radius": "15px",
            "box-shadow": "0 4px 12px rgba(0,0,0,0.2)"
        }
    )
    container_content.append(top_section)
    
    # --- Main Menu Display (สำหรับแสดงข้อมูลเท่านั้น) ---
    menu_names = [food.get_name() for food in boxset.get_fixed_menu()]
    background_color = "#f2f1ec"
    container_content.append(
        H1(f"{boxset_name}", style={"text-align": "center", "margin-top": "40px", "margin-bottom": "40px"})
    )
    container_content.append(
        Card(
            H3("Main menu", style=f"background-color: {background_color}; padding: 15px; color: #000000; text-align: left; margin-left: -18px;"),
            *[P(menu, style={"font-size": "18px", "margin": "5px 0"}) for menu in menu_names],
            style=f"""
                width: 100%;
                min-height: 200px;
                padding: 20px;
                margin: 10px 0;
                background-color: {background_color};
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            """
        )
    )
    container_content.append(H3("Select Menu", style={"text-align": "center", "margin-top": "30px", "margin-bottom": "30px"}))
    
    # --- Form Section: รวม dropdown สำหรับเลือกเมนู และ input hidden สำหรับ counter ---
    form_content = []
    for selected in boxset.get_box_select_list():
        grid_content = [
            Grid(H3(f"{selected.get_menu_type()}", style="color: black; background-color: #f2f1ec   ; padding: 10px; border-radius: 5px; text-align: left"))
        ]
        options = [Option(food.get_name()) for food in selected.get_select_option()]
        grid_content.append(
            Card(
                Select(*options, name=f"select_{selected.get_menu_type()}", style="""
                    padding: 10px; 
                    width: 100%; 
                    margin-bottom: 20px; 
                    border-radius: 5px; 
                    border: 1px solid #ccc;
                """),
                style="display: flex; justify-content: center; margin-bottom: 10px;"
            )
        )
        form_content.extend(grid_content)
    
    # เพิ่ม input hidden สำหรับ counter value ลงใน form
    form_content.append(
         Input(id="form_counter_value", type="hidden", name="counter_value", value="1")
    )
    # เพิ่มปุ่ม submit ลงใน form
    form_content.append(
         Button("Select", type="submit", style={
             "background-color": "#FF3333", 
             "color": "white", 
             "padding": "10px 20px", 
             "border-radius": "5px", 
             "border": "none", 
             "cursor": "pointer",
             "font-size": "18px"
         })
    )
    
    form = Form(*form_content, method="post", action=f"/submit/{boxset.get_boxset_id()}")
    container_content.append(form)
    
    # ปุ่ม "GO Back"
    container_content.append(
         A(Button("GO Back"), href="/menu", style={"display": "block", "margin": "20px auto"})
    )
    
    # --- Script: อัปเดต counter และอัปเดต input hidden ใน form ---
    container_content.append(
        Script("""
            let counterValue = 1;  // Initialize counter with 1
            document.getElementById("counter").innerText = counterValue;
            function updateCounter(action) {
                if (action === 'increase') {
                    counterValue++;
                } else if (action === 'decrease' && counterValue > 1) {
                    counterValue--;
                }
                document.getElementById("counter").innerText = counterValue;
                document.getElementById("form_counter_value").value = counterValue;
            }
        """)
    )
    return Container(*container_content)

@rt("/submit/{boxset_id}", methods=["POST"])
def post(boxset_id: str, select_menu: dict, counter_value: int):
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    
    if isinstance(member,Manager):
        return Redirect("/menu")
    
    select_menu.popitem() #ลบและคืนค่าตัวสุดท้าย
    
    # ดึงข้อมูลเมนูที่เลือก
    selected_foods = [select_menu[key] for key in select_menu]
    
    # ใช้ค่าจำนวนที่ส่งมา
    system.choose_boxset(boxset_id, selected_foods, counter_value)

    return Redirect("/menu")

@rt("/food/{food_id}")
def food_detail(food_id: str):
    food = system.search_food_by_id(food_id)
    if not food:
        return P("Food not found.")
    
    food_name = food.get_name()
    container_content = [
        navbar(),       
        order_section(),
    ]
    
    # --- Top Section: แสดงภาพและ counter (สำหรับการแสดงผลเท่านั้น) ---
    top_section = Div(
        # ด้านซ้าย: แสดงภาพ
        Div(
            Img(
                src=food.get_picture(),  
                style={
                    "width": "30vw",      
                    "height": "50vh", 
                    "object-fit": "cover",
                    "border-radius": "8px",
                    "margin": "30px",
                }
            ),
            style={"flex": "1", "text-align": "center"}
        ),
        # ด้านขวา: แสดงชื่อเซต, ราคา (ถ้ามี) และ counter
        Div(
            Div(
                H1(food_name, style={"margin-bottom": "20px"}),
                Button("+", onclick="updateCounter('increase')", style={
                    "background": "#4CAF50", 
                    "border": "none", 
                    "color": "white", 
                    "font-size": "24px", 
                    "cursor": "pointer", 
                    "padding": "10px 20px",
                    "border-radius": "20px", 
                    "box-shadow": "0 4px 6px rgba(0,0,0,0.3)"
                }),
                Span(id="counter", style={
                    "margin": "0 20px", 
                    "font-size": "24px", 
                    "font-weight": "bold"
                }),
                Button("-", onclick="updateCounter('decrease')", style={
                    "background": "#f44336", 
                    "border": "none", 
                    "color": "white", 
                    "font-size": "24px", 
                    "cursor": "pointer", 
                    "padding": "10px 20px",
                    "border-radius": "20px", 
                    "box-shadow": "0 4px 6px rgba(0,0,0,0.3)"
                }),
                style={
                    "text-align": "center", 
                    "margin-bottom": "10px",
                    "background": "white",
                    "height": "40vh",
                    "width": "40vw",
                    "border-radius": "10px",
                    "box-shadow": "0 4px 10px rgba(0,0,0,0.2)",
                    "display": "flex",
                    "flex-direction": "column",
                    "justify-content": "center",
                    "align-items": "center"
                }
            ),
            style={
                "flex": "1", 
                "text-align": "center",
                "display": "flex", 
                "flex-direction": "column", 
                "align-items": "center"
            }
        ),
        style={
            "background-color": "#f2f1ec",
            "display": "flex", 
            "width": "100%", 
            "justify-content": "space-around", 
            "align-items": "center",
            "padding": "20px",
            "box-sizing": "border-box",
            "border-radius": "15px",
            "box-shadow": "0 4px 12px rgba(0,0,0,0.2)"
        }
    )
    container_content.append(top_section)
    
    # --- Main Menu Display (สำหรับแสดงข้อมูลเท่านั้น) ---
    background_color = "#dbf8cc"
    container_content.append(
        H1(f"{food_name}", style={"text-align": "center", "margin-top": "20px"})
    )
    
    # --- Form Section: รวม dropdown สำหรับเลือกเมนู และ input hidden สำหรับ counter ---
    form_content = []

    # ตรวจสอบว่า food เป็น Drink
    if isinstance(food,Drink):
        level_content = ["ไม่หวาน", "หวานน้อย", "ปกติ", "หวานมาก"]
    elif isinstance(food,Savory):
        level_content = ["ไม่เผ็ด" , "เผ็ดน้อย" , "เผ็ดมาก" , "เผ็ดมากสุดๆ" , "เผ็ดนรก"]

    if food.get_select():
        grid_content = [
            Grid(H3(f"Level", style="color: black; background-color: #f2f1ec; padding: 10px; border-radius: 5px; text-align: left"))
        ]
        options = [Option(level) for level in level_content]  # แก้ไข options
        grid_content.append(
            Card(
                Select(*options, name="select_sweet_level", style=""" 
                    padding: 10px; 
                    width: 100%; 
                    margin-bottom: 20px; 
                    border-radius: 5px; 
                    border: 1px solid #ccc;
                """),
                style="display: flex; justify-content: center; margin-bottom: 10px;"
            )
        )
        form_content.extend(grid_content)
    
    # เพิ่ม input hidden สำหรับ counter value ลงใน form
    form_content.append(
        Input(id="form_counter_value", type="hidden", name="counter_value", value="1")
    )
    
    # เพิ่มปุ่ม submit ลงใน form
    form_content.append(
        Button("Select", type="submit", style={
            "background-color": "#FF3333", 
            "color": "white", 
            "padding": "10px 20px", 
            "border-radius": "5px", 
            "border": "none", 
            "cursor": "pointer",
            "font-size": "18px"
        })
    )
    
    form = Form(*form_content, method="post", action=f"/submit_food/{food.get_food_id()}")
    container_content.append(form)
    
    # --- Script: อัปเดต counter และอัปเดต input hidden ใน form ---
    container_content.append(
        Script("""
            let counterValue = 1;  // Initialize counter with 1
            document.getElementById("counter").innerText = counterValue;
            function updateCounter(action) {
                if (action === 'increase') {
                    counterValue++;
                } else if (action === 'decrease' && counterValue > 1) {
                    counterValue--;
                }
                document.getElementById("counter").innerText = counterValue;
                document.getElementById("form_counter_value").value = counterValue;
            }
        """)
    )
    return Container(*container_content)


@rt("/submit_food/{food_id}", methods=["POST"])
def post_food(food_id: str, select_menu: dict):
    member = session.get_current_user()
    
    if isinstance(member,Manager):
        return Redirect("/menu")
    
    if not member:
        return Redirect("/fail")  # ถ้าไม่มีผู้ใช้ใน session ให้ไปที่หน้าล้มเหลว
    
    # ตรวจสอบข้อมูลจาก select_menu
    counter_value = select_menu.get('counter_value', 1)  # ถ้าไม่มี 'counter_value' ให้ใช้ค่าเริ่มต้นเป็น 1
    level = select_menu.get('select_sweet_level', None)  # ค่าเริ่มต้นเป็น 'ปกติ'
    
    # ส่งข้อมูลไปที่ system.choose_menu
    system.choose_menu(food_id, counter_value, level)
    
    # เปลี่ยนไปที่หน้ารายการเมนูอาหาร
    return Redirect("/menu")  # ✅ เปลี่ยนไปหน้ารายการเมนูอาหาร

@rt("/")
def get():
    grid_content = [
        navbar(),  # เรียกใช้ Navbar
        order_section(),  # เรียกใช้ Order Section
    ]
    
    # ตั้งค่า CSS สำหรับฟอนต์และสไตล์ของปุ่ม
    button_style = {
        "background": "linear-gradient(135deg, #e83120, #ff6347)",  # สีพื้นหลังที่เป็นการไล่สี
        "border": "2px solid #8B0000",  # กำหนดเส้นขอบสีแดงเข้ม
        "border-radius": "50%",  # ให้ปุ่มเป็นวงกลม
        "color": "#ffebeb",  # สีของข้อความในปุ่ม
        "font-size": "16px",  # ขนาดตัวอักษร
        "cursor": "pointer",  # เปลี่ยนเป็นรูปมือเมื่อชี้
        "padding": "0px",  # ช่องว่างภายในปุ่ม
        "width": "40px",  # ความกว้าง
        "height": "40px",  # ความสูง
        "text-align": "center",  # จัดข้อความให้อยู่กลาง
        "line-height": "40px",  # จัดข้อความให้อยู่กลางปุ่ม
        "position": "absolute",  # ให้ปุ่มลอยอยู่บนภาพ
        "transition": "all 0.3s ease-in-out",  # เพิ่มการเปลี่ยนแปลงแบบราบรื่น
        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.3)",  # เพิ่มเงาใต้ปุ่ม
        "font-family": "'K2D', sans-serif",  # กำหนดฟอนต์
    }
    
    grid_content.append(
        Div(
            Img(id="image", src="https://downloads.ctfassets.net/n4pc9wlortyn/7Hi5tth6sQ1MMpOfDivJPr/477ea208c5ac40e615f0131d9ec4a0cf/Buldak_Sauce_Mar25_Desktop_2880x1740.png"),  # เริ่มต้นแสดงภาพแรก
            Div(
                Button("01", onclick="changeImage(1);", style={**button_style, "bottom": "45px", "left": "70px"}),
                Button("02", onclick="changeImage(2);", style={**button_style, "bottom": "45px", "left": "130px"}),
                Button("03", onclick="changeImage(3);", style={**button_style, "bottom": "45px", "left": "190px"}),
                Button("04", onclick="changeImage(4);", style={**button_style, "bottom": "45px", "left": "250px"}),
                cls="button-container",
                style={ 
                    "position": "relative",  # กำหนดให้ container ของปุ่มเป็นตำแหน่ง relative
                    "width": "100%",  # ให้ container กว้างเต็ม
                    "height": "100%"  # ให้ container สูงเต็ม
                }
            ),
            # เพิ่ม div สำหรับแสดงคำพูด
            Div(id="text-content-1",  # ตั้งชื่อ id ของข้อความที่ 1
                style={ 
                    "position": "absolute", 
                    "bottom": "180px", 
                    "left": "50px", 
                    "color": "white", 
                    "font-size": "70px", 
                    "font-family": "'K2D', sans-serif",  # ใช้ฟอนต์ K2D
                    "font-weight": "600"
                }, 
                children=["บูลดัก ดังก์วิงซ์"]
            ),
            Div(id="text-content-2",  # ตั้งชื่อ id ของข้อความที่ 2
                style={ 
                    "position": "absolute", 
                    "bottom": "180px", 
                    "left": "70px", 
                    "color": "white", 
                    "font-size": "70px", 
                    "font-family": "'K2D', sans-serif",  # ใช้ฟอนต์ K2D
                    "font-weight": "600"
                }, 
                children=["ดีลผู้พัน แชร์กันวันพฤหัส"]  # เปลี่ยนข้อความที่สอง
            ),
            Div(id="text-content-3",  # ตั้งชื่อ id ของข้อความที่ 3
                style={ 
                    "position": "absolute", 
                    "bottom": "180px", 
                    "left": "50px", 
                    "color": "white", 
                    "font-size": "70px", 
                    "font-family": "'K2D', sans-serif",  # ใช้ฟอนต์ K2D
                    "font-weight": "600"
                }, 
                children=["ดีลลับวันอังคาร 10 ชิ้น 199 .-"]  # เปลี่ยนข้อความที่สาม
            ),
            Div(id="text-content-4",  # ตั้งชื่อ id ของข้อความที่ 4
                style={ 
                    "position": "absolute", 
                    "bottom": "170px", 
                    "left": "70px", 
                    "color": "white", 
                    "font-size": "70px", 
                    "font-family": "'K2D', sans-serif",  # ใช้ฟอนต์ K2D
                    "font-weight": "600"
                }, 
                children=["ชิคแอนด์แชร์ ชุดละ 99 .-"]  # เปลี่ยนข้อความที่สี่
            ),
            # ใส่ JavaScript เพื่อเปลี่ยนรูปภาพและคำพูด
            Script("""
                let currentIndex = 1;

                function changeImage(choice) {
                    var imageUrl = "";
                    var textContent1 = "";
                    var textContent2 = "";
                    var textContent3 = "";
                    var textContent4 = "";

                    switch(choice) {
                        case 1:
                            imageUrl = "https://downloads.ctfassets.net/n4pc9wlortyn/7Hi5tth6sQ1MMpOfDivJPr/477ea208c5ac40e615f0131d9ec4a0cf/Buldak_Sauce_Mar25_Desktop_2880x1740.png";
                            textContent1 = "บูลดัก ดังก์วิงซ์";
                            break;
                        case 2:
                            imageUrl = "https://images.ctfassets.net/n4pc9wlortyn/1WdsRSUTMDM6rzLrXr9uxe/b19a227e4e93f4a1a73ebf6165e06eef/DV_THURSDAY_Mar25_Desktop_2880x1240.png";
                            textContent2 = "ดีลผู้พัน<br>แชร์กันวันพฤหัส";
                            break;
                        case 3:
                            imageUrl = "https://downloads.ctfassets.net/n4pc9wlortyn/2F3PSaIg8slNmrEkHmmhYz/57c4e2efd510616b0a296f27281f3366/DV_Tue_DESKTOP_IMAGE_2880x1260px.png";
                            textContent3 = "ดีลลับวันอังคาร<br>10 ชิ้น 199 .-";
                            break;
                        case 4:
                            imageUrl = "https://downloads.ctfassets.net/n4pc9wlortyn/5QekPE09zRFUAD9JmX4wUS/5bc5e6da51fd4d461c9f590ca4d1c11b/KFC_DEC_Campaign_Chick_n__Share_Web_and_App_Banner_2880x1260px.png";
                            textContent4 = "ชิคแอนด์แชร์<br>ชุดละ 99 .-";
                            break;
                    }

                    // ตั้งค่า opacity ของรูปให้เป็น 0 ก่อนการเปลี่ยนรูป
                    document.getElementById("image").style.opacity = 0.7;  // ทำให้ภาพจางลงเล็กน้อย

                    // รีเซ็ตแอนิเมชัน fade
                    document.getElementById("text-content-1").style.animation = 'none';
                    document.getElementById("text-content-2").style.animation = 'none';
                    document.getElementById("text-content-3").style.animation = 'none';
                    document.getElementById("text-content-4").style.animation = 'none';

                    // เพิ่ม animation fade-out ก่อนที่จะเฟด in ข้อความใหม่
                    document.getElementById("text-content-1").style.animation = 'fadeOut 2s ease-in-out';
                    document.getElementById("text-content-2").style.animation = 'fadeOut 2s ease-in-out';
                    document.getElementById("text-content-3").style.animation = 'fadeOut 2s ease-in-out';
                    document.getElementById("text-content-4").style.animation = 'fadeOut 2s ease-in-out';

                    // รีเฟรชแอนิเมชัน fade
                    setTimeout(function() {
                        // ตั้งค่า opacity ของรูปให้กลับมาเป็น 1 (ทำให้รูปค่อยๆ เฟดขึ้น)
                        document.getElementById("image").src = imageUrl;
                        document.getElementById("image").style.opacity = 1;  // กลับมาแสดงผลปกติ

                        // รีสตาร์ทการแสดงข้อความใหม่ด้วย fade-in
                        document.getElementById("text-content-1").style.animation = 'fadeIn 2s ease-in-out';
                        document.getElementById("text-content-2").style.animation = 'fadeIn 2s ease-in-out';
                        document.getElementById("text-content-3").style.animation = 'fadeIn 2s ease-in-out';
                        document.getElementById("text-content-4").style.animation = 'fadeIn 2s ease-in-out';

                        // อัพเดตข้อความ
                        document.getElementById("text-content-1").innerText = textContent1;
                        document.getElementById("text-content-2").innerHTML = textContent2;
                        document.getElementById("text-content-3").innerHTML = textContent3;
                        document.getElementById("text-content-4").innerHTML = textContent4;

                    }, 1000);  // ตั้งเวลาให้มีช่วงเวลารอประมาณ 1 วินาที ก่อนเริ่มเฟด

                    // เพิ่ม delay ให้ข้อความถัดไป
                    setTimeout(function() {
                        document.getElementById("text-content-2").style.animation = 'fadeIn 1s ease-in-out';
                        document.getElementById("text-content-3").style.animation = 'fadeIn 1s ease-in-out';
                        document.getElementById("text-content-4").style.animation = 'fadeIn 1s ease-in-out';
                    }, 3000);  // เพิ่ม delay 2 วินาที ก่อนแสดงข้อความที่ 2-4
                }

                changeImage(currentIndex);
                setInterval(function() {
                    currentIndex = (currentIndex % 4) + 1;  // ให้เลือกเป็นลำดับที่ 1-4
                    changeImage(currentIndex);
                }, 6000);  // ทุก 5000 มิลลิวินาที (5 วินาที)
            """),
            Style("""
                @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600&display=swap');
                
                html, body {
                    background: white;
                }

                /* @keyframes สำหรับการเฟดข้อความ */
                @keyframes fadeIn {
                    0% {
                        opacity: 0;
                    }
                    100% {
                        opacity: 1;
                    }
                }

                @keyframes fadeOut {
                    0% {
                        opacity: 1;
                    }
                    100% {
                        opacity: 0;
                    }
                }

                /* เพิ่ม animation-delay ให้กับข้อความแต่ละตัว */
                #text-content-1 {
                    animation-delay: 0s;
                }

                #text-content-2 {
                    animation-delay: 2s;  /* เพิ่ม delay */
                }

                #text-content-3 {
                    animation-delay: 4s;  /* เพิ่ม delay */
                }

                #text-content-4 {
                    animation-delay: 6s;  /* เพิ่ม delay */
                }

                .button-container button:hover {
                    transform: scale(1.4);  /* ขยายขนาดปุ่มเมื่อ hover */
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.5);  /* เพิ่มเงาเมื่อ hover */
                    transition: all 0.3s ease-in-out;  /* เพิ่ม transition เพื่อให้การเปลี่ยนแปลงนุ่มนวล */
                    background: #360000;  /* เปลี่ยนพื้นหลังเมื่อ hover */
                    border-color: #b22222;  /* เปลี่ยนขอบเมื่อ hover */
                }

                /* เพิ่มสีเมื่อเมาส์ชี้ที่ปุ่ม */
                .button-container button:active {
                    background: #b22222;  /* เปลี่ยนพื้นหลังเมื่อกด */
                    color: white;  /* เปลี่ยนสีข้อความเมื่อกด */
                }

                /* เพิ่มการแสดงผลของข้อความที่ค่อยๆ เฟดขึ้น */
                #text-content-1, #text-content-2, #text-content-3, #text-content-4 {
                    animation: fadeIn 2s ease-in-out;  /* เพิ่มแอนิเมชันให้ข้อความค่อยๆ เฟด */
                }

                #image {
                    transition: opacity 1.5s ease-in-out;  /* เพิ่ม transition ให้กับ opacity */
                    opacity: 1;  /* ให้ภาพแสดงผลอย่างชัดเจน */
                }
            """)
        )
    )

    return grid_content

@rt("/menu")
def get():
    member = session.get_current_user()
    menu = system.get_boxset_list()
    
    # สร้าง Grid ของ Boxset แต่ละอัน
    grid_content = [
        navbar(),  # เรียกใช้ Navbar
        order_section(),  # เรียกใช้ Order Section
        Div(  # หัวข้อของหน้า
            H2("Box Set Menu", style={"text-align": "center", "margin-top": "40px", "font-size": "40px"}),
            style={"width": "100%"}
        )
    ]
    if isinstance(member,Manager):
        grid_content = [ managebar()
    ]
        grid_content.append(Div(
        H3("WELCOME MANAGER", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
            ))
    # ใช้ Grid Layout เพื่อจัดเรียงการ์ดให้สวย
    boxset_grid = Grid(
        *[
            Card(
                H3(boxset.get_name(), style={"color": "black", "font-size": "20px", "margin-bottom": "10px"}),
                P(f"Price: {boxset.get_price()} THB", style={"color": "#666", "font-size": "16px"}),
                P(f"Main menu: {', '.join([food.get_name() for food in boxset.get_fixed_menu()])}",
                  style={"color": "#444", "font-size": "14px"}),
                A(
                    Button("Select", style={
                        "background": "green",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 20px",
                        "cursor": "pointer",
                        "border-radius": "5px"
                    }), 
                    href=f"/boxset/{boxset.get_boxset_id()}"
                ),
                style={
                    "background-color": "white",
                    "border": "1px solid #ddd",
                    "border-radius": "10px",
                    "padding": "20px",
                    "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "display": "flex",
                    "flex-direction": "column",
                    "align-items": "center",
                    "gap": "10px",
                    "text-align": "center",
                    "width": "250px"
                }
            ) for boxset in menu
        ],
        style={
            "display": "grid",
            "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",  # จัดให้การ์ดเรียงในรูปแบบ Grid
            "gap": "20px",
            "padding": "20px",
            "justify-content": "center"
        }
    )

    grid_content.append(boxset_grid)
    grid_content.append(
        Div(  # หัวข้อของหน้า
            H2("Menu", style={"text-align": "center", "margin-bottom": "40px" , "font-weight" : "750", "font-size" : "50px"}),
            style={"width": "100%"}
        )
    )
    menu_type = [Savory, Dessert, Drink]

    for type in menu_type:
        menu_in_type = []  # ✅ ย้ายเข้าไปในลูปเพื่อเคลียร์ค่าเก่า
    
        grid_content.append(H2(type.__name__, style={"text-align": "center", "margin-bottom": "20px"}))  # ✅ แก้ type เป็นชื่อคลาส
    
        for menu in system.get_menu_list():
            if isinstance(menu, type):
                menu_in_type.append(menu)

        menu_grid = Grid(
            *[
                Card(
                    H3(food.get_name(), style={"text-align": "center", "margin-bottom": "20px"}),
                    P(f"Price: {food.get_price()} THB", style={"color": "#666", "font-size": "16px"}),
                    A(
                        Button("Select", style={
                        "background": "green",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 20px",
                        "cursor": "pointer",
                        "border-radius": "5px"
                        }), 
                        href=f"/food/{food.get_id()}"  # ✅ เปลี่ยนจาก boxset.get_boxset_id() เป็น food.get_id()
                    ),
                    style={
                        "background-color": "white",
                        "border": "1px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                        "display": "flex",
                        "flex-direction": "column",
                        "align-items": "center",
                        "gap": "10px",
                        "text-align": "center",
                        "width": "250px"
                    }
                ) for food in menu_in_type
            ],
            style={
                "display": "grid",
                "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",
                "gap": "20px",
                "padding": "20px",
                "justify-content": "center"
            }
        )

        grid_content.append(menu_grid)  # ✅ เพิ่ม Grid ลงไปใน grid_content



    
    return Container(
        *grid_content
    )


@rt("/basket")
def view_basket(coupon_code: str = ""):
    print(f"Received Coupon Code: {coupon_code}")  # Debugging

    member = session.get_current_user()

    if not member:
        return Redirect('/fail')

    basket = member.get_current_basket().check_empty()



    if basket:
        items, total_price, discount_applied, discount_include = member.view_basket(coupon_code)
        order_type_text = None
        if isinstance(member.get_order_type(), Delivery):
            order_type_text = H2("Order Type : Delivery",style={"margin-top": "10px", "margin-bottom": "20px"})    
        elif isinstance(member.get_order_type(), PickUp):
             order_type_text = H2("Order Type : Pickup",style={"margin-top": "10px", "margin-bottom": "20px"}) 
        else:
            order_type_text = H2("PLEASE SELECT ORDER TYPE",style={"margin-top": "10px", "margin-bottom": "20px"})
        
        
        return Container(
            
        navbar(),  
        order_section(),  
        
    H1("Your Basket",style={"margin-top": "20px", "margin-bottom": "50px"}),
    order_type_text,
    Grid(
        *[
            Card(
                H3(item["name"].get_name()),
                P(f"Quantity: {item['quantity']}"),
                P(f"{item['name'].get_price()} THB"),
                # ตรวจสอบและแสดงระดับความหวานหรือความเผ็ด
                *[
                    P(f"Sweets Level: {item["name"].get_select()}") if (isinstance(item["name"],Drink)) and (item["name"].get_select()) else None,
                    P(f"Spiciness Level: {item["name"].get_select()}") if (isinstance(item["name"],Savory)) and (item["name"].get_select()) else None,
                    P(f"Select menu: {item["name"].get_selected_menu()}") if (isinstance(item["name"],Boxset)) else None,
                ]
            )
            for item in items
        ]
    ),
    Form(
        Label("Enter coupon code", Input(name="coupon_code", placeholder="Coupon code", value=coupon_code)),
        Button("Use Code"),
        method="get",
        action="/basket"
    ),
    Div(
        H3(f"Total Price (Before Discount): {total_price:.2f} THB",style={"margin-top": "30px", "margin-bottom": "10px"}),
        H3(f"Discount Applied: {discount_applied:.2f} THB",style={"margin-top": "30px", "margin-bottom": "10px"}),
        H3(f"Total After Discount: {discount_include:.2f} THB",style={"margin-top": "30px", "margin-bottom": "30px"}),
        Button("Checkout", onclick="window.location='/payment'", style="background-color: green; color: white; padding: 10px 20px; border: none;")
    ),
)
    else:
        grid_content = [
    navbar(),  # เรียกใช้ Navbar
    order_section(),  # เรียกใช้ Order Section
]

    grid_content.append(
    Div(
        # พื้นหลังสี่เหลี่ยม
        Div(
            # รูปภาพ (อยู่ซ้าย)
            Img(
                id="image",
                src="https://www.kfc.co.th/static/media/empty_cart.32f17a45.png",
                style={
                    "width": "200px",  # กำหนดขนาดรูป
                    "height": "200px",
                    "object-fit": "contain",  # ป้องกันภาพผิดสัดส่วน
                    "margin-right": "20px"  # เว้นระยะระหว่างรูปกับข้อความ
                }
            ),
            # ข้อความ (อยู่ขวา)
            Div(
                H3("Basket is empty", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "24px",
                    "margin": "0"
                }),
                P("Your shopping cart is currently empty.", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "16px",
                    "margin-top": "5px"
                }),
                style={
                    "display": "flex",
                    "flex-direction": "column",  # ให้ข้อความอยู่เป็นแนวตั้ง
                    "justify-content": "center"  # จัดให้อยู่ตรงกลางแนวตั้ง
                }
            ),
            style={
                "display": "flex",
                "align-items": "center",  # จัดให้รูปและข้อความอยู่ตรงกลางแนวตั้ง
                "background": "#ff0000",  # สีพื้นหลัง (สีแดง)
                "padding": "20px",  # เพิ่มระยะห่างภายใน
                "border-radius": "10px",  # ขอบมน
                "width": "60%",  # กำหนดความกว้างของกล่อง
                "margin": "auto",  # จัดให้อยู่ตรงกลางของหน้าจอ
                "box-shadow": "0px 4px 10px rgba(0,0,0,0.2)"  # เพิ่มเงาให้ดูสวยงาม
            }
        ),
        style={
            "display": "flex",
            "justify-content": "center",  # จัดให้อยู่กลางหน้าจอ
            "align-items": "center",
            "height": "100vh",  # ให้เต็มจอแนวตั้ง
            "background": "#f4f4f4"  # สีพื้นหลังของหน้าจอ
        }
    )
)


    return grid_content

@rt('/selectdelivery')
def order_type():
    grid_content = [ navbar()

    ]
    grid_content.append(Div(
        # Navbar - แยกออกจาก Order Container
        

        # Title Section
        H1("เลือกช่องทางการรับออเดอร์", cls="title"),

        # Styling for the page
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

            html, body {
                background: #ffffff;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                font-family: 'TH Sarabun', sans-serif;
                display: flex;
                flex-direction: column;  /* ปรับให้เนื้อหาตั้งอยู่ในรูปแบบคอลัมน์ */
                text-align: center;
                overflow: hidden;
            }

            .title {
                font-size: 40px;
                font-weight: 700;
                color: #000000;
                margin-top: 150px;  # ลดระยะห่างจากด้านบนให้เหมาะสม
            }

            .order-container {
                width: 400px;
                padding: 400px;
                display: flex;
                flex-direction: column;
                align-items: center; /* จัดแนวตั้งกลาง */
                gap: 40px;
                height: 200px;
                margin-top: -150px;  # ปรับให้เนื้อหาคล่องตัวมากขึ้น
            }

            .order-button1 {
                width: 250px;
                height: 60px;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                border: 2px solid #000000; /* กรอบสีดำ */
                background: #ffffff; /* พื้นหลังสีขาว */
                color: #000000; /* ตัวอักษรสีดำ */
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-left : 740px;
                margin-top : -150px;
            }

            .order-button1:hover {
                background: #f0f0f0; /* พื้นหลังสีเทาอ่อนเมื่อ hover */
                transform: scale(1.05);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            }

            .order-button1:active {
                transform: scale(0.95);
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
            }
            .order-button2 {
                width: 250px;
                height: 60px;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                border: 2px solid #000000; /* กรอบสีดำ */
                background: #ffffff; /* พื้นหลังสีขาว */
                color: #000000; /* ตัวอักษรสีดำ */
                border-radius: 10px;
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-left : 740px;
            }

            .order-button2:hover {
                background: #f0f0f0; /* พื้นหลังสีเทาอ่อนเมื่อ hover */
                transform: scale(1.05);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            }

            .order-button2:active {
                transform: scale(0.95);
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
            }
        """),

        # Order Buttons Section
        Div(
            Button("🚚 รับที่ร้าน", onclick="window.location.href='/pickup';", cls="order-button1"),
            Button("🏡 เดลิเวอรี่", onclick="window.location.href='/delivery';", cls="order-button2"),
            cls="order-container"
        )
    )
    )
    return grid_content

@rt('/pickup')
def get():
    
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    
    pickup = session.get_current_user().add_order_type(PickUp())
    return Titled("เลือกสาขา",
    Style(""" 
        @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

        html, body {
            background: #ffffff;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            font-family: 'TH Sarabun', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: -30px;
        }

        .title {
            font-size: 40px;
            font-weight: 700;
            color: #000000;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
        }

        .search-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            margin-top: 30px;
        }
        .select-button {
            width: 180px; /* ลดขนาดความกว้างลง */
            height: 50px; /* ขนาดความสูงคงที่ */
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            border: 1px solid #000000; /* กรอบสีดำ */
            background: #ffffff; /* พื้นหลังสีขาว */
            color: #000000; /* ตัวอักษรสีดำ */
            border-radius: 8px; /* มุมปุ่มโค้ง */
            cursor: pointer;
            box-shadow: 0px 5px 10px rgba(0, 0, 0, 0.2); /* เงาลดลงเล็กน้อย */
            transition: all 0.3s ease-in-out;
        }

        .select-button:hover {
            background: #f0f0f0;
            transform: scale(1.05);
            box-shadow: 0px 8px 15px rgba(0, 0, 0, 0.3);
        }

        .select-button:active {
            transform: scale(0.95);
            box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.2);
        }
          
        .input-postcode {
            width: 400px !important;
            height: 50px !important;
            font-size: 18px !important;
            padding: 10px !important;
            border-radius: 10px !important;
            border: 1px solid #ddd !important;
            background-color: #ffffff !important;
            color: #333 !important;
        }

        .input-postcode::placeholder {
            color: #333 !important;
        }

        .input-postcode:focus {
            background-color: #f0f0f0 !important;
            border: 1px solid #000 !important;
        }

        .search-button {
            width: 250px;
            height: 60px;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            border: 2px solid #000000;
            background: #ffffff;
            color: #000000;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease-in-out;
        }

        .search-button:hover {
            background: #f0f0f0;
            transform: scale(1.05);
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
        }

        .search-button:active {
            transform: scale(0.95);
            box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
        }

        .branch-card {
            background: white;
            padding: 20px;
            margin: 15px auto;
            width: 90%;
            max-width: 500px;
            border-radius: 12px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #ff0000;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .branch-card:hover {
            transform: translateY(-5px);
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
        }

        .done-button {
            width: 250px;
            height: 60px;
            font-size: 22px;
            font-weight: bold;
            text-align: center;
            border: 2px solid #000000;
            background: #ffffff;
            color: #000000;
            border-radius: 10px;
            cursor: pointer;
            box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease-in-out;
            margin-top: 20px;
        }

        .done-button:hover {
            background: #f0f0f0;
            transform: scale(1.05);
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
        }

        .done-button:active {
            transform: scale(0.95);
            box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
        }

        .no-branch-card {
            color: #333;
            margin: 10px;
            margin-top: 40px;
            margin-bottom: 40px;
            font-family: 'TH Sarabun', sans-serif;
        }
    """),
    Form(Input(id="postcode", placeholder="กรอกรหัสไปรษณีย์...", name="postcode",required=True, cls="input-postcode"), 
         hx_get="/search", target_id="results", hx_trigger="keyup delay:200ms"),
    Div(id="results"),
    H3("สาขาที่เลือก :"),
    Div(B("ยังไม่ได้เลือกสาขา"), id="selected_branch", cls="no-branch-card"),
    Button("เสร็จสิ้น", onclick="window.location.href='/menu';", cls="done-button"),
)

@rt('/delivery')
def delivery_page():
    
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    
    session.get_current_user().add_order_type(Delivery())
    return Titled("ที่อยู่จัดส่ง",
        Style("""
                @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

                html, body {
                    background: #ffffff;
                    min-height: 100vh;
                    margin: 0;
                    padding: 0;
                    font-family: 'TH Sarabun', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    margin-top: -100px;
                }

                .title {
                    font-size: 40px;
                    font-weight: 700;
                    color: #000000;
                    text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                }

                .delivery-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 20px;
                    margin-top: 100px;
                }

                .delivery-input {
                    width: 400px;
                    height: 50px;
                    font-size: 18px;
                    padding: 10px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    background-color: #ffffff;
                    color: #333;
                    box-sizing: border-box;
                    margin-top: 70px;
                }

                .delivery-input::placeholder {
                    color: #333;
                }

                .delivery-input:focus {
                    background-color: #f0f0f0;
                    border: 1px solid #000;
                }

                .done-button {
                    width: 250px;
                    height: 60px;
                    font-size: 22px;
                    font-weight: bold;
                    text-align: center;
                    border: 2px solid #000000;
                    background: #ffffff;
                    color: #000000;
                    border-radius: 10px;
                    cursor: pointer;
                    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                    transition: all 0.3s ease-in-out;
                    margin-top: 50px;
                }

                .done-button:hover {
                    background: #f0f0f0;
                    transform: scale(1.05);
                    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
                }

                .done-button:active {
                    transform: scale(0.95);
                    box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
                }

                .address-confirmation {
                    font-size: 18px;
                    color: #333;
                    margin-top: 20px;
                    font-weight: 500;
                }
        """),
        Form(
            Input(id="delivery_address", placeholder="กรอกที่อยู่จัดส่งของคุณ...", name="address",required=True, cls="delivery-input"),
            Button("ยืนยัน", cls="done-button"),
            method='post',
            action="/submit_address"
        ),
        Div(id="address_confirmation"),
    )



@rt('/submit_address')
def submit_address(address: str):
    
    
    delivery = session.get_current_user().get_order_type()
    

    delivery.set_address(address)
    
    print(f"Address entered: {delivery.get_address()}")
    return Redirect("/menu")
    
@rt('/select_delivery')
def select_delivery():
    delivery = session.get_current_user().get_order_type()
    return Titled("Delivery Information",
        H3(f"Delivery Address: {delivery.get_address()}"),
        Button("Done", onclick="window.location.href='/menu';", cls = "done-button"),
    )

@rt('/search')
def search(postcode: Optional[str] = None):
    if not postcode or not postcode.strip().isdigit():
        return B("กรุณากรอกรหัสไปรษณีย์เป็นตัวเลข")
    result = system.search_branches(postcode.strip())
    return Div(result)


@rt('/fail')
def get():
    grid_content = [
            navbar(),  # เรียกใช้ Navbar
            order_section(),  # เรียกใช้ Order Section
        ]

    grid_content.append(
        Div(
            # พื้นหลังสี่เหลี่ยม
                Div(
            # รูปภาพ (อยู่ซ้าย)
                Img(
                    id="image",
                    src="https://www.kfc.co.th/static/media/empty_cart.32f17a45.png",
                    style={
                    "width": "200px",  # กำหนดขนาดรูป
                    "height": "200px",
                    "object-fit": "contain",  # ป้องกันภาพผิดสัดส่วน
                    "margin-right": "20px"  # เว้นระยะระหว่างรูปกับข้อความ
                    }
                ),
                # ข้อความ (อยู่ขวา)
                Div(
                    H3("PLEASE LOG IN FIRST", style={
                        "color": "white",  # ตัวอักษรสีขาว
                        "font-size": "24px",
                        "margin": "0"
                    }),
                    P("OR SIGN IN.", style={
                        "color": "white",  # ตัวอักษรสีขาว
                        "font-size": "16px",
                        "margin-top": "5px"
                    }),
                    style={
                        "display": "flex",
                        "flex-direction": "column",  # ให้ข้อความอยู่เป็นแนวตั้ง
                        "justify-content": "center"  # จัดให้อยู่ตรงกลางแนวตั้ง
                    }
                ),
                style={
                    "display": "flex",
                    "align-items": "center",  # จัดให้รูปและข้อความอยู่ตรงกลางแนวตั้ง
                    "background": "#ff0000",  # สีพื้นหลัง (สีแดง)
                    "padding": "20px",  # เพิ่มระยะห่างภายใน
                    "border-radius": "10px",  # ขอบมน
                    "width": "60%",  # กำหนดความกว้างของกล่อง
                    "margin": "auto",  # จัดให้อยู่ตรงกลางของหน้าจอ
                    "box-shadow": "0px 4px 10px rgba(0,0,0,0.2)"  # เพิ่มเงาให้ดูสวยงาม
                }
            ),
            style={
                "display": "flex",
                "justify-content": "center",  # จัดให้อยู่กลางหน้าจอ
                "align-items": "center",
                "height": "100vh",  # ให้เต็มจอแนวตั้ง
                "background": "#f4f4f4"  # สีพื้นหลังของหน้าจอ
            }
        )
        )   
    return grid_content

@rt('/select_branch')
def select_branch(district: str, address: str ):
    pickup = session.get_current_user().get_order_type()
    branch_info = {"district": district , "address": address}
    if branch_info == None:
        Redirect("/pickup")
    pickup.set_branch(branch_info)
    return B(f"{district} ({address})")

@rt("/login")
def get():
    grid_content = [
    navbar(),  # เรียกใช้ Navbar
    order_section(),  # เรียกใช้ Order Section
    ]
    grid_content.append(Container(
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

            html, body {
                background: #ffffff;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                font-family: 'TH Sarabun', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                text-align: center;
            }

            .login-title {
                font-size: 42px;
                font-weight: 800;
                color: #000000;
                margin-top: 30px;
            }

            .login-form {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 25px;
                margin-top: 20px;
            }

            .input-username, .delivery-input {
                width: 400px;
                height: 50px;
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                background-color: #ffffff;
                color: #333;
                box-sizing: border-box;
            }

            .input-username::placeholder,
            .delivery-input::placeholder {
                color: #333;
            }

            .input-username:focus,
            .delivery-input:focus {
                background-color: #f0f0f0;
                border: 1px solid #000;
            }

            .login-submit-button {
                width: 250px;
                height: 60px;
                font-size: 22px;
                font-weight: bold;
                text-align: center;
                border: none;                          /* ไม่มีเส้นขอบ */
                background: #cccccc;                   /* สีเทาอ่อน */
                color: #3d3c3c;
                border-radius: 50px;                   /* <<< ทำให้เป็นวงรี */
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-top: 40px;
            }

            .login-submit-button:hover {
                background: #bbbbbb;                   /* สีเทาเข้มขึ้นเล็กน้อยตอน hover */
                transform: scale(1.01);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            }

            .login-submit-button:active {
                transform: scale(0.95);
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
            }

            .username-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
            }
            .password-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
        """),
        H1("เข้าสู่ระบบ", cls="login-title"),
        Form(
            Div(
                Label("Username:", For="username", cls="username-label"),
                Input(type="text", id="username", placeholder="กรอกชื่อผู้ใช้งาน...", required=True, cls="input-username"),
                cls="login-form"
            ),
            Div(
                Label("Password:", For="password", cls="password-label"),
                Input(type="password", id="password", placeholder="กรอกรหัสผ่าน...", required=True, cls="delivery-input"),
                cls="login-form"
            ),
            Button("เข้าสู่ระบบ", type="submit", cls="login-submit-button"),
            method="post",
            action="/login/submit"
        )
    )
    )
    return grid_content 

@rt("/register")
def get():
    grid_content = [
        navbar(),  # เรียกใช้ Navbar
        order_section(),  # เรียกใช้ Order Section
    ]
    grid_content.append(Container(
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

            html, body {
                background: #ffffff;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                font-family: 'TH Sarabun', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                text-align: center;
                overflow-x: hidden;

            }

            .register-title {
                font-size: 42px;
                font-weight: 800;
                color: #000000;
                margin-top: 30px;
            }

            .register-form {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 25px;
                margin-top: 20px;
            }

            .input-field {
                width: 400px;
                height: 50px;
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                background-color: #ffffff;
                color: #333;
                box-sizing: border-box;
            }

            .input-field::placeholder {
                color: #333;
            }

            .input-field:focus {
                background-color: #f0f0f0;
                border: 1px solid #000;
            }

            .register-submit-button {
                width: 200px;
                height: 50px;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                border: none;
                background: #cccccc;
                color: #3d3c3c;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-top: 40px;
            }

            .register-submit-button:hover {
                background: #bbbbbb;
                transform: scale(1.01);
                box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            }

            .register-submit-button:active {
                transform: scale(0.95);
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
            }
            .name-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            .surname-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            .phone-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            .email-label {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            .username-label2 {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            .password-label2 {
                color : #3d3c3c;
                margin-top: 20px;
                text-align: left;
                display: block;            /* ให้ label แสดงเต็มบรรทัด */
                width: 100%;               /* ขยาย label ให้กว้างเต็มบรรทัด */
                padding-left: 10px;        /* (ถ้าอยากมีระยะห่างเล็กน้อยจากซ้าย) */
                box-sizing: border-box;
                margin-top: -10px;
            }
            
            
            
        """),
        H1("สร้างบัญชีผู้ใช้", cls="register-title"),
        Form(
            Div(
                Label("Name:", cls="name-label"),
                Input(type="text", id="name", placeholder="ชื่อจริง", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("Surname:", cls="surname-label"),
                Input(type="text", id="surname", placeholder="นามสกุล", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("Phone Number:", cls="phone-label"),
                Input(type="text", id="tel_number", placeholder="หมายเลขโทรศัพท์", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("Email:", cls="email-label"),
                Input(type="email", id="email", placeholder="อีเมล", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("Username:", cls="username-label2"),
                Input(type="text", id="username", placeholder="ชื่อ Username", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("Password:", cls="password-label2"),
                Input(type="password", id="password", placeholder="รหัสผ่าน", required=True, cls="input-field"),
                cls="register-form"
            ),
            Button("สร้างบัญชี", type="submit", cls="register-submit-button"),
            method="post",
            action="/register/submit"
        )
    ))
    return grid_content

@rt("/login/submit")
def post(username: str, password: str):
    return system.handle_authentication("login", username=username, password=password)

@rt("/register/submit")
def post(name: str, surname: str, tel_number: str, email: str, username: str, password: str):
    return system.handle_authentication("register", name, surname, tel_number, email, username, password)

@rt('/payment')
def get():
    member = session.get_current_user()
    if member.get_order_type() == None:
        return Redirect("/selectdelivery")
    
    grid_content = [navbar(), order_section()]
    
    grid_content.append(
        Div(
            Style(""" 
                @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

                html, body {
                    background: #ffffff;
                    min-height: 100vh;
                    margin: 0;
                    padding: 0;
                    font-family: 'TH Sarabun', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }

                .payment-container {
                    display: flex;
                    align-items: center;
                    background: #f2f1ec;
                    padding: 40px;
                    border-radius: 10px;
                    width: 80%; /* เพิ่มขนาดกล่อง */
                    margin: auto;
                    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
                    flex-direction: column;
                }

                .payment-title {
                    font-size: 60px; /* ขยายขนาดข้อความ */
                    font-weight: 800;
                    color: #000000;
                    margin-bottom: 50px;
                }

                .payment-options {
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: center;
                    gap: 80px;
                }

                .payment-button {
                    width: 300px;
                    height: 60px;
                    font-size: 18px;
                    font-weight: bold;
                    text-align: center;
                    border: none;
                    background: rgb(209, 209, 209);
                    color: rgb(0, 0, 0);
                    border-radius: 50px;
                    cursor: pointer;
                    box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                    transition: all 0.3s ease-in-out;
                }

                .payment-button:hover {
                    background: rgb(253, 255, 239);
                    transform: scale(1.01);
                    box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
                }

                .payment-button:active {
                    transform: scale(0.95);
                    box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.2);
                }
            """),
            H1("วิธีการชำระเงิน", cls="payment-title"),
            Div(
                A(Button("🧾 ชำระด้วย QR Code", cls="payment-button"), href='/QR'),
                A(Button("💳 ชำระเงินด้วยบัตรเครดิต", cls="payment-button"), href='/account_num'),
                cls="payment-options"
            ),
            cls="payment-container"
        )
    )
    
    return grid_content

@rt('/QR')
def get():
    member = session.get_current_user()
    grid_content = [
            navbar(),  # เรียกใช้ Navbar
            order_section(),  # เรียกใช้ Order Section
        ]

    grid_content.append(
        Div(
            # พื้นหลังสี่เหลี่ยม
                Div(
            # รูปภาพ (อยู่ซ้าย)
                Img(
                    id="image",
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/330px-QR_code_for_mobile_English_Wikipedia.svg.png",
                    style={
                    "width": "200px",  # กำหนดขนาดรูป
                    "height": "200px",
                    "object-fit": "contain",  # ป้องกันภาพผิดสัดส่วน
                    "margin-right": "20px"  # เว้นระยะระหว่างรูปกับข้อความ
                    }
                ),
                # ข้อความ (อยู่ขวา)
                Div(
                    P('สแกนเพื่อชำระเงิน', style ='font-size: 50px'),
                    P(f"Price: {member.get_current_basket().calculate_total_price()}"),
                    Button('ชำระเงินเสร็จสิ้น',hx_post=f'/total/order/{member.get_id}',style="background-color: green; color: white; padding: 10px 20px; border: none;")
                   
                    
                ),
                style={
                    "display": "flex",
                    "align-items": "center",  # จัดให้รูปและข้อความอยู่ตรงกลางแนวตั้ง
                    "background": "#f2f1ec",  # สีพื้นหลัง (สีแดง)
                    "padding": "20px",  # เพิ่มระยะห่างภายใน
                    "border-radius": "10px",  # ขอบมน
                    "width": "60%",  # กำหนดความกว้างของกล่อง
                    "margin": "auto",  # จัดให้อยู่ตรงกลางของหน้าจอ
                    "box-shadow": "0px 4px 10px rgba(0,0,0,0.2)"  # เพิ่มเงาให้ดูสวยงาม
                }
            ),
            style={
                "display": "flex",
                "justify-content": "center",  # จัดให้อยู่กลางหน้าจอ
                "align-items": "center",
                "height": "100vh",  # ให้เต็มจอแนวตั้ง
                "background": "#f4f4f4"  # สีพื้นหลังของหน้าจอ
            }
        )
        )   
    return grid_content

@rt('/account_num')
def get():
    member = session.get_current_user()
    
    grid_content = [
        navbar(),  # Navbar
        order_section(),  # Order Section
    ]

    grid_content.append(Container(
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

            html, body {
                background: #ffffff;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                font-family: 'TH Sarabun', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                text-align: center;
                overflow-x: hidden;
            }

            .register-title {
                font-size: 42px;
                font-weight: 800;
                color: #000000;
                margin-top: 30px;
            }

            .register-form {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                margin-top: 20px;
            }

            .input-field {
                width: 400px;
                height: 50px;
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                background-color: #ffffff;
                color: #333;
                box-sizing: border-box;
            }

            .input-field::placeholder {
                color: #333;
            }

            .input-field:focus {
                background-color: #f0f0f0;
                border: 1px solid #000;
            }

            .register-submit-button {
                width: 200px;
                height: 50px;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                border: none;
                background: #28a745;
                color: white;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-top: 20px;
            }

            .register-submit-button:hover {
                background: #218838;
                transform: scale(1.02);
            }

            .register-submit-button:active {
                transform: scale(0.95);
            }

            .label {
                color: #3d3c3c;
                text-align: left;
                display: block;
                width: 100%;
                padding-left: 10px;
                box-sizing: border-box;
                margin-top: -10px;
            }
        """),
        H1("ชำระเงินด้วยบัตรเครดิต", cls="register-title"),
        P(f"Price: {member.get_current_basket().calculate_total_price()}"),
        Form(
            Div(
                Label("ชื่อ:", cls="label"),
                Input(type="text", name="first_name", placeholder="ชื่อ", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("นามสกุล:", cls="label"),
                Input(type="text", name="last_name", placeholder="นามสกุล", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("เลขบัตรเครดิต:", cls="label"),
                Input(type="text", name="credit_card", placeholder="เลขบัตรเครดิต", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("CVV:", cls="label"),
                Input(type="password", name="cvv", placeholder="CVV", required=True, cls="input-field"),
                cls="register-form"
            ),
            Button('ชำระเงินเสร็จสิ้น', type="submit", cls="register-submit-button"),
            method="post",
            action=f"/total/order/{member.get_id}",
            cls="register-form"
        )
    ))

    return grid_content


@rt('/total/order/{member_id}')
def post(member_id: str):
    
    return Redirect('/summary')

@rt('/summary')
def summary_page():
    member = session.get_current_user()
    order_delivery_by = None
    order_type = member.get_order_type()
    branch = order_type.get_branch()
    branch_info = branch.get_branch_address()

    bg_color = "#fffafa"
    text_color = "#000000"
    card_bg = "#d4d4d4"
    card_text = "#000000"
    border_color = "#ffffff"

    summary = system.summary_order()
    if not summary:
        return H1("Member not found", style=f"color: red; text-align: center;")
    rider = None
    if isinstance(order_type,Delivery):
        
        rider = system.find_free_rider(order_type)
        rider_name = rider.get_account_name()
        member_address = order_type.get_address()
        order_delivery_by = Div(P(f"Delivery by: {rider_name}", style=f"color: {card_text};"),
        P(f"FROM BRANCH: {branch_info}", style=f"color: {card_text};"),
        P(f"Address: {member_address}", style=f"color: {card_text};"))
        type = "Delivery"
        if rider == "Busy":
            order_delivery_by = P(f"PLEASE WAIT FOR RIDER", style=f"color: {card_text};"),

    elif isinstance(order_type,PickUp):
        order_delivery_by = P(f"Branch: {branch_info}", style=f"color: {card_text};"),
        type = "Pickup At Store"

    order = member.create_order_history(rider)
    manage_stock = system.manage_stock(branch)

    user_info, items, total_price, order_type, discount_applied = summary

    
    
    member_info_group = Card(
        H2("Customer Information", style=f"margin-bottom: 15px; color: #000000;"),
        Div(
            P(f"Name: {user_info[0]} {user_info[1]}", style=f"color: {card_text};"),
            P(f"Order Type: {type}", style=f"color: {card_text};"),
            P(f"Phone Number: {user_info[3]}", style=f"color: {card_text};"),
            P(f"Order ID: {order.get_order_id()}", style=f"color: {card_text};"),
            order_delivery_by,
            style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;"
        ),
        style=f"padding: 20px; margin-bottom: 20px; background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 10px;"
    )

    basket_group = Grid(
        *[
            Card(

                H3(item["name"].get_name(), style=f"margin-bottom: 5px; color: #000000;"),
                P(f"Quantity: {item['quantity']} pcs", style=f"color: {card_text};"),
                P(f"Unit Price: {item["name"].get_price()} THB", style=f"color: {card_text};"),
                P(f"Subtotal: {int(item["name"].get_price()) * int(item['quantity'])} THB", style=f"color: {card_text};"),
                *[
                    P(f"Sweets Level: {item["name"].get_select()}") if (isinstance(item["name"],Drink)) and (item["name"].get_select()) else None,
                    P(f"Spiciness Level: {item["name"].get_select()}") if (isinstance(item["name"],Savory)) and (item["name"].get_select()) else None,
                    P(f"Select menu: {item["name"].get_selected_menu()}") if (isinstance(item["name"],Boxset)) else None
                ],
                style=f"padding: 15px; background-color: {card_bg}; border: 1px solid {border_color}; border-radius: 8px;"
            )
            for item in items
        ],
        style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;"
    )

    H3(f"Price", style=f"margin-bottom: 10px; color:#ff3333;")
    coupon_and_total_group = Card(
        
        H2(f"Discount Applied: {discount_applied} THB", style=f"color: #000000;"),
        H2(f"Total Price: {total_price} THB", style=f"color: #000000;"),
        style=f"padding: 20px; background-color: {card_bg}; border-radius: 10px;"
    )
    return Container(
        H1("Order Summary", style=f"text-align: center; color: {text_color};"),
        member_info_group,
        H2("Items in Basket", style="color: #000000;"),
        basket_group,
        coupon_and_total_group,
        Div(
            Button("Back to Home", onclick="window.location='/'", style="background-color: red; color: white; padding: 10px 20px; border: none; border-radius: 5px;"),
            Button("New Order", onclick="window.location='/neworder'", style="background-color: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; margin-left: 10px;"),
            style="text-align: center; margin-top: 20px;"
        ),
            style=f"padding: 30px; background-color: {bg_color};"
        )
@rt("/neworder")
def get():
    member = session.get_current_user()
    member.make_new_order()
    return Redirect("/menu")


@rt("/account")
def get(): 
    grid_content = []
    unique_accounts = set()  # ใช้เซ็ตเพื่อลบค่าซ้ำ

    for account in system.get_member_list():
        account_tuple = (account.get_account_name(), account.get_account_surname(), account.get_email())

        if account_tuple not in unique_accounts:
            unique_accounts.add(account_tuple)
            grid_content.append(
                Card(
                    P(account_tuple[0]),
                    P(account_tuple[1]),
                    P(account_tuple[2])
                )
            )

    return Container(Grid(*grid_content))

@rt("/manager")
def get():
    grid_content = [ managebar()
]
    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    ))

    grid_content.append(
    Div(
        # พื้นหลังสี่เหลี่ยม
        Div(
            # รูปภาพ (อยู่ซ้าย)
            Img(
                id="image",
                src="https://www.kfc.co.th/static/media/empty_cart.32f17a45.png",
                style={
                    "width": "200px",  # กำหนดขนาดรูป
                    "height": "200px",
                    "object-fit": "contain",  # ป้องกันภาพผิดสัดส่วน
                    "margin-right": "20px"  # เว้นระยะระหว่างรูปกับข้อความ
                }
            ),
            # ข้อความ (อยู่ขวา)
            Div(
                H3("WELCOME MANAGER!", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "24px",
                    "margin": "0"
                }),
                P("OUR SERVICE IS FOR CUSTOMERS.", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "16px",
                    "margin-top": "5px"
                }),
                style={
                    "display": "flex",
                    "flex-direction": "column",  # ให้ข้อความอยู่เป็นแนวตั้ง
                    "justify-content": "center"  # จัดให้อยู่ตรงกลางแนวตั้ง
                }
            ),
            style={
                "display": "flex",
                "align-items": "center",  # จัดให้รูปและข้อความอยู่ตรงกลางแนวตั้ง
                "background": "#ff0000",  # สีพื้นหลัง (สีแดง)
                "padding": "20px",  # เพิ่มระยะห่างภายใน
                "border-radius": "10px",  # ขอบมน
                "width": "60%",  # กำหนดความกว้างของกล่อง
                "margin": "auto",  # จัดให้อยู่ตรงกลางของหน้าจอ
                "box-shadow": "0px 4px 10px rgba(0,0,0,0.2)"  # เพิ่มเงาให้ดูสวยงาม
            }
        ),
        style={
            "display": "flex",
            "justify-content": "center",  # จัดให้อยู่กลางหน้าจอ
            "align-items": "center",
            "height": "100vh",  # ให้เต็มจอแนวตั้ง
            "background": "#f4f4f4"  # สีพื้นหลังของหน้าจอ
        }
    )
)
    return grid_content

@rt("/delete_item/{item_id}/{item_type}")
def delete_item(item_id: str, item_type: str):
    
    member = session.get_current_user()
    if not isinstance(member,Manager):
        return Redirect("/fail")  # กรณีไม่ได้ล็อกอิน
    system.delete_item_by_id(item_id, item_type, member) 
    return Redirect("/manage_menu") 
    

@rt("/manage_menu")
def get():
    menu = system.get_boxset_list()
    
    # สร้าง Grid ของ Boxset แต่ละอัน
    grid_content = [
    managebar()
]

    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    ))
    grid_content.append(
        Div(
            H2("Manage Individual Menu", style={"text-align": "center", "margin-bottom": "20px"}),
            H2("Boxset", style={"text-align": "center", "margin-bottom": "20px"}),
            style={"width": "100%"}
        )
    )
    # ใช้ Grid Layout เพื่อจัดเรียงการ์ดให้สวย
    boxset_grid = Grid(
        *[
            Card(
                H3(boxset.get_name(), style={"color": "black", "font-size": "20px", "margin-bottom": "10px"}),
                P(f"Price: {boxset.get_price()} THB", style={"color": "#666", "font-size": "16px"}),
                P(f"Main menu: {', '.join([food.get_name() for food in boxset.get_fixed_menu()])}",
                  style={"color": "#444", "font-size": "14px"}),

                # ปุ่ม Delete
                A(
                    Button("Delete", style={
                        "background": "red",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 20px",
                        "cursor": "pointer",
                        "border-radius": "5px"
                    }),
                    href=f"/delete_item/{boxset.get_boxset_id()}/boxset"
                ),

                style={
                    "background-color": "white",
                    "border": "1px solid #ddd",
                    "border-radius": "10px",
                    "padding": "20px",
                    "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "display": "flex",
                    "flex-direction": "column",
                    "align-items": "center",
                    "gap": "10px",
                    "text-align": "center",
                    "width": "250px"
                }
            ) for boxset in menu
        ],
        style={
            "display": "grid",
            "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",
            "gap": "20px",
            "padding": "20px",
            "justify-content": "center"
        }
    )

    grid_content.append(boxset_grid)
    

    menu_type = [Savory, Dessert, Drink]

    for type in menu_type:
        menu_in_type = []

        grid_content.append(H2(f"{type.__name__} Menu", style={"text-align": "center", "margin-bottom": "20px"}))

        for menu in system.get_menu_list():
            if isinstance(menu, type):
                menu_in_type.append(menu)
    
        menu_grid = Grid(
            *[
                Card(
                    H3(food.get_name(), style={"text-align": "center", "margin-bottom": "20px"}),
                    P(f"Price: {food.get_price()} THB", style={"color": "#666", "font-size": "16px"}),

                    # ปุ่ม Delete
                    A(
                        Button("Delete", style={
                            "background": "red",
                            "color": "white",
                            "border": "none",
                            "padding": "10px 20px",
                            "cursor": "pointer",
                            "border-radius": "5px"
                        }), 
                        href=f"/delete_item/{food.get_food_id()}/food"
                    ),

                    style={
                        "background-color": "white",
                        "border": "1px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                        "display": "flex",
                        "flex-direction": "column",
                        "align-items": "center",
                        "gap": "10px",
                        "text-align": "center",
                        "width": "250px"
                    }
                ) for food in menu_in_type
            ],
            style={
                "display": "grid",
                "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",
                "gap": "20px",
                "padding": "20px",
                "justify-content": "center"
            }
        )

        grid_content.append(menu_grid)

    return Container(*grid_content)

@rt("/restore/menu/{menu_id}")
def restore_menu(menu_id: str):
    member = session.get_current_user()
    if not isinstance(member,Manager):
        return Redirect("/fail")  # กรณีไม่ได้ล็อกอิน

    result = system.restore_item(menu_id, member)
    return result  # กลับไปที่หน้าจัดการเมนู



@rt("/restore_delete_menu")
def get():
    menu = system.get_delete_menu() or []  # ป้องกันกรณี None
    delete_boxset = [item for item in menu if isinstance(item, Boxset)]
    delete_menu = [item for item in menu if isinstance(item, Food)]

    grid_content = [managebar()]

    # คำเตือน
    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
            "color": "red",
            "font-size": "24px",
            "padding": "10px 20px",
        }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
        }
    ))
    grid_content.append(
        Div(
            H2("Manage Individual Menu", style={"text-align": "center", "margin-bottom": "20px"}),
            H2("Boxset", style={"text-align": "center", "margin-bottom": "20px"}),
            style={"width": "100%"}
        )
    )
    # Grid ของ Boxset
    boxset_grid = Grid(
        *[
            Card(
                H3(boxset.get_name(), style={"font-size": "20px"}),
                P(f"Price: {boxset.get_price()} THB"),
                P(f"Main menu: {', '.join([food.get_name() for food in (boxset.get_fixed_menu() or [])])}"),
                A(
                    Button("Restore", style={"background": "green", "color": "white", "padding": "10px"}),
                    href=f"/restore/menu/{boxset.get_boxset_id()}"
                ),
                style={"border": "1px solid #ddd", "padding": "20px", "text-align": "center"}
            ) for boxset in delete_boxset
        ],
        style={"display": "grid", "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))"}
    )

    grid_content.append(boxset_grid)

    # แสดงเมนูแต่ละประเภท
    menu_type = [Savory, Dessert, Drink]
    for type in menu_type:
        menu_in_type = [food for food in delete_menu if isinstance(food, type)]
        
        if menu_in_type:
            grid_content.append(H2(f"{type.__name__} Menu"))

            menu_grid = Grid(
                *[
                    Card(
                        H3(food.get_name()),
                        P(f"Price: {food.get_price()} THB"),
                        A(
                            Button("Restore", style={"background": "green", "color": "white"}),
                            href=f"/restore/menu/{food.get_food_id()}"
                        ),
                        style={"border": "1px solid #ddd", "padding": "20px", "text-align": "center"}
                    ) for food in menu_in_type
                ],
                style={"display": "grid", "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))"}
            )
            grid_content.append(menu_grid)

    return Container(*grid_content)

def Card(*children, **kwargs):
    return Div(*children, **kwargs)

def Container(*children, **kwargs):
    return Div(*children, **kwargs)

def Grid(*children, **kwargs):
    return Div(*children, **kwargs)



serve()
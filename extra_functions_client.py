import mysql.connector as mysql
from itertools import product

db=mysql.connect(host="localhost",user="root",password="mysql",database="hydrateproducts")

db_cursor=db.cursor()


# Get image links

def get_image_dict(id):
    def MySQL_get_images(id):
        filtered_images = []
        db_cursor.execute("Select clr1,clr2,clr3,clr4,clr5,clr6,clr7,clr8,clr9,clr10 from productimages where id={};".format(id))
        for i in db_cursor.fetchone():
            if i is not None:
                filtered_images.append(i)
        return filtered_images

    def image_link_unpack(image_link):
        a = image_link.split("::::")
        d = {}
        d[a[0]] = a[1].replace("[", "").replace("]", "").split(",")
        return d

    imageDict = {}
    for i in MySQL_get_images(id):
        unpacked_image = image_link_unpack(i)
        for key in unpacked_image:
            imageDict[key] = unpacked_image[key]

    return imageDict



# Get product details

def get_product_details(id):
    
    def MySQL_get_product_details(id):
        query="""
        SELECT 
        pd.desc1, pd.desc2, pd.desc3, pd.spec1, pd.spec2, 
        ps.S, ps.M, ps.L, ps.XL, ps.XXL, ps.custom
        FROM 
        productdetail pd
        INNER JOIN 
        productsizes ps ON pd.id = ps.id
        WHERE 
        pd.id = {};""".format(id)
        
        
        db_cursor.execute(query)
        result = db_cursor.fetchone()
        
        if result:
            desc = [result[0], result[1], result[2]]
            spec = [result[3],result[4]]
            sizes= {
                "S":result[5],
                "M":result[6],
                "L":result[7],
                "XL":result[8],
                "XXL":result[9],
                "custom":result[10]
            }
            
            desc = [d for d in desc if d is not None]
            spec = [s for s in spec if s is not None]
            final_spec=""
            if len(spec)!=1:
                final_spec=spec[0]+"||"+spec[1]
            else:
                final_spec=spec[0]
            product_details = {
                "desc": desc,
                "spec": spec_data_unpack(final_spec),
                "size": sizes
            }
        else:
            product_details = {
                "desc": [],
                "spec": [],
                "size":{}
            }
        
        return product_details

    def spec_data_unpack(a):
        spec_dict={}
        x=a.split("||")
        for i in x:
            datasplit=i.split(";:")
            spec_dict[datasplit[0]]=datasplit[1]
        return spec_dict
    try:
        data=MySQL_get_product_details(id)
        return data
    except Exception as e:
        return {"error":e}


# Get product list

def colour_unpack(data):
    final_unpacked = []
    try:
        for i in data:
            try:
                if len(i) > 4:
                    i[4] = i[4].split("||")
                else:
                    raise IndexError("List does not have enough elements to access index 4.")
                final_unpacked.append(i)
            except IndexError as e:
                print(f"Index error: {e} in list {i}")
            except AttributeError as e:
                print(f"Attribute error: {e}. Ensure the element at index 4 is a string.")
            except Exception as e:
                print(f"Error processing list {i}: {e}")
    except Exception as e:
        print(f"Error in colour_unpack: {e}")
    return final_unpacked


def category_sorted_list(unsorted_list, keyword):
    def sort_key(item):
        return item["category"] != keyword

    sorted_list = sorted(unsorted_list, key=sort_key)
    
    return sorted_list


def get_products_list(keyword):

    def MySQL_get_products_list(keyword):

        try:
            similar_keywords =list(generate_combinations(keyword))
            similar_keywords.append(keyword)
            similar_keywords.append(keyword.replace('-', " "))

            query = f"""
            SELECT *
            FROM products
            WHERE category='{keyword}'
            """
            for i in similar_keywords:
                query += f"OR title LIKE '%{i}%'\n"
            query += ";"

            db_cursor.execute(query)
            result = db_cursor.fetchall()
            tup_to_list = [list(i) for i in result]
            colour_unpacked_list=colour_unpack(tup_to_list)
            list_to_dict=[]
            for i in colour_unpacked_list:
                temp_dict={}
                temp_dict["id"]=i[0]
                temp_dict["title"]=i[1]
                temp_dict["price"]=i[2]
                temp_dict["category"]=i[3]
                temp_dict["colors"]=i[4]
                temp_dict["thumbnail"]=i[5]
                temp_dict["tagline1"]=i[6]
                temp_dict["tagline2"]=i[7]
                temp_dict["material"]=i[8]
                list_to_dict.append(temp_dict)
            
            return category_sorted_list(list_to_dict,keyword)

        except Exception as e:
            print(f"Error in MySQL_get_products_list: {e}")
            return []

    def generate_combinations(word):
        try:
            def case_combinations(word):
                return map(''.join, product(*((c.upper(), c.lower()) for c in word)))
            
            base_combinations = set(case_combinations(word))
            
            result = set()
            for comb in base_combinations:
                parts = comb.split()
                if len(parts) > 1:
                    for i in range(1, len(parts)):
                        combined = ' '.join(parts[:i]) + '-' + ' '.join(parts[i:])
                        result.add(combined)
                result.add(comb.replace(' ', ''))
            
            return result
        except Exception as e:
            print(f"Error in generate_combinations: {e}")
            return set()

    try:
        return MySQL_get_products_list(keyword=keyword)
    except Exception as e:
        print(f"Error in get_products_list: {e}")
        return []

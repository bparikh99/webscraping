import requests
import os
from bs4 import BeautifulSoup
from mdutils.mdutils import MdUtils



def make_call(year,month):
    post_links=[]
    try:
        res=requests.get(f"https://sathyasaiwithstudents.blogspot.com/{year}/{month}")
    
        if res.status_code==200:
            soup=BeautifulSoup(res.text,"html.parser")
            try:
               post_links=[i.find("a")['href'] for i in soup.find("ul",class_="posts").find_all("li")]
            except AttributeError:
                print("Attribut not available")
        else:
            print("Eror status code "+ str(res.status_code))
    except:
        print("Error while extracting Data from URL")
    return post_links


def extract_details(post_link):

    images=[]
    text_data=[]
    filtered_tags=[]
    file,title="",""
    try:
        res=requests.get(post_link)
        if res.status_code==200:
            soup=BeautifulSoup(res.text,"html.parser")
            # text_data=[i.get_text() for i in soup.find("div",class_="widget Blog").find_all("p",attrs={"style":"text-align: justify;"})]
            text_lst=[""+"^"+i.get_text() if i.findChildren("table")  else i.get_text() for i in soup.find("div",class_="widget Blog").find_all("p",attrs={"style":"text-align: justify;"})]
            for text in text_lst:
                if text.startswith("^"):
                    text_data.extend(text.split("^"))
                else:
                    text_data.append(text)
            title=soup.find("title").get_text()
            images=soup.find("div",class_="widget Blog").find_all("img")[:-1]
            file=post_link.split("/")[-1].split(".")[0]
            tags=[tag.get_text(strip=True) for tag in soup.find("span",class_="post-labels").find_all("a")]
            filtered_tags=[i.split(".")[-1].strip() if "." in i else i for i in tags ]
        else:
            print("Eror status code "+ str(res.status_code))
    except Exception as e:
        print("Error while extracting from individual link"+ str(e))

    return text_data,images,file,title,filtered_tags

def make_markdown(file,write_path,text_data,title,filtered_tags,count,year_path,post_link):

    try:     
        markdown_path=write_path+"\\"+year_path+"\\"+file+"\\"+file
        mdFile = MdUtils(file_name=markdown_path+"temp.md")
        count=count+1
        format_data="---"+"\n"
        val_title='title: "{0}"'.format(title)
        count=count+1
        year=year_path.split("\\")[0]
        month=year_path.split("\\")[1]
        date_val=f"{year}-{month}-{count}"
        date="date: {0}".format(date_val)
        oldUrl="oldUrl: {0}".format(post_link)

        mdFile.new_line(format_data+val_title)
        mdFile.new_line(date)
        mdFile.new_line(oldUrl)
        mdFile.new_line("tags:")
        mdFile.new_list(items=filtered_tags,marked_with="  -")      
        mdFile.write(format_data)
        for text in text_data:
            if ".jpg" in text:
                mdFile.new_line(mdFile.new_inline_image(text="image", path=text))
            else:
                mdFile.new_paragraph(text)
            mdFile.write('\n')
        mdFile.create_md_file()
        md_data=mdFile.read_md_file(markdown_path+"temp.md")
        md_data=md_data.lstrip("\n").strip().lstrip("\n")
        with open(markdown_path+".md" ,"w") as final_data:
            final_data.write(md_data)

        #os.rename(markdown_path+"temp.md", markdown_path+".md")
        os.remove(markdown_path+"temp.md")
    except Exception as e:
        print("Error while writing data for markdown file "+str(e))

def extract_images(images,write_path,file,empty_text,year_path):
  
    try:
        jpg_folder=write_path+"\\"+year_path+"\\"+file+"\\"+"images"
        if not os.path.exists(jpg_folder):
            os.makedirs(jpg_folder)

        for img in range(len(images)):
            res=requests.get(images[img]['src'])        
            img_path=jpg_folder+"\\"+"img"+str(img)+".jpg"

            with open(img_path,"wb") as data:
                data.write(res.content)
                
    except Exception as e:
        print("Error while writing data for image file "+ str(e))
        
    img_files=os.listdir(jpg_folder)
    for text in text_data:
        if text=="":
            text_index=text_data.index(text)
            try:
                local_img_path="images"+"/"+img_files[empty_text-1]
                text_data[text_index]=local_img_path
                empty_text=empty_text+1
            except:
                pass
            
    return text_data

        
    

if __name__ == "__main__":
    path=os.getcwd()
    write_path=path+"\\"+"main"

    if not os.path.exists(write_path):
        os.mkdir(write_path)
    else:
        print("path exists")
    os.chdir(write_path)
    year=int(input("Enter Year between 2012 -2021 : "))
    month=input("Enter Month : ")
    if len(month)==1:
        month="0"+month
        
    
    print(f"Downloading Posts for year: {year}, month: {month}")

    post_links=make_call(year,month)
    year_path=str(year)+"\\"+str(month)
    print("Total no of links found "+str(len(post_links)))
    for count,post_link in enumerate(post_links):
        print(f"Downloading {count}/{len(post_links)} Posts")
        empty_text=1
        text_data, images, file, title, filtered_tags=extract_details(post_link)
        filtered_data=extract_images(images,write_path,file,empty_text,year_path)
        make_markdown(file,write_path,text_data,title,filtered_tags,count,year_path,post_link)

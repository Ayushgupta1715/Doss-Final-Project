import tkinter as tk
import pywhatkit
from geopy.geocoders import ArcGIS
import cv2
import boto3
import wikipediaapi
import cohere
import webbrowser


#For GenAI
def open_genai_window():
    genai_window = tk.Toplevel()
    genai_window.title("GenAI")

    def get_wikipedia_summary(query):
        user_agent = "MyApp/1.0 (nd4157958@gmail.com)"
        wiki_wiki = wikipediaapi.Wikipedia(language='en', extract_format=wikipediaapi.ExtractFormat.WIKI, user_agent=user_agent)
        page = wiki_wiki.page(query)
        if page.exists():
            return page.summary
        else:
            return "No page found for the given query."

    def generate_text(prompt, cohere_client):
        response = cohere_client.generate(
            model='command-medium-nightly',
            prompt=prompt,
            max_tokens=10
        )
        return response.generations[0].text.strip()

    def main(query):
        cohere_client = cohere.Client('CvST2CbR7Zl6zEuF4hVMTPFPbwVesH9g2o9GK3QK')
        wiki_summary = get_wikipedia_summary(query)
        wiki_summary_label.config(text="Wikipedia Summary:\n" + wiki_summary)
        cohere_response = generate_text(wiki_summary, cohere_client)
        cohere_response_label.config(text="Cohere Response:\n" + cohere_response)

    query_label = tk.Label(genai_window, text="Enter your query:")
    query_label.grid(row=0, column=0, padx=10, pady=5)
    query_entry = tk.Entry(genai_window)
    query_entry.grid(row=0, column=1, padx=10, pady=5)

    submit_button = tk.Button(genai_window, text="Submit", command=lambda: main(query_entry.get()))
    submit_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5)

    wiki_summary_label = tk.Label(genai_window, text="", wraplength=400, justify=tk.LEFT)
    wiki_summary_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

    cohere_response_label = tk.Label(genai_window, text="", wraplength=400, justify=tk.LEFT)
    cohere_response_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)


#For Managing instances
def open_instances_window():
    instances_window = tk.Toplevel()
    instances_window.title("EC2 Instances Management")

    # AWS EC2 client
    ec2 = boto3.client('ec2')

    # Function to list running instances
    def list_running_instances():
        response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
        instances = response.get('Reservations', [])
        if instances:
            instance_info = "\n".join([f"{i}. Instance ID: {instance['Instances'][0]['InstanceId']}" for i, instance in enumerate(instances, start=1)])
            instances_text.config(state=tk.NORMAL)
            instances_text.delete("1.0", tk.END)
            instances_text.insert(tk.END, f"Running Instances:\n{instance_info}")
            instances_text.config(state=tk.DISABLED)
        else:
            instances_text.config(state=tk.NORMAL)
            instances_text.delete("1.0", tk.END)
            instances_text.insert(tk.END, "No running instances found.")
            instances_text.config(state=tk.DISABLED)

    # Function to start or launch instances
    def launch_instance():
        try:
            no = int(instance_count_entry.get())
            if no <= 0:
                raise ValueError("Number of instances should be a positive integer.")
            for _ in range(no):
                ec2.run_instances(ImageId='ami-0a0f1259dd1c90938',
                                  InstanceType='t2.micro',
                                  MinCount=1,
                                  MaxCount=1)
            list_running_instances()
            success_label.config(text=f"{no} instance(s) launched successfully!", fg="green")
        except ValueError as ve:
            success_label.config(text=str(ve), fg="red")

    # Function to stop instances
    def stop_instances():
        try:
            instance_number = int(stop_instance_entry.get()) - 1
            if instance_number < 0:
                raise ValueError("Instance number should be a positive integer.")
            response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            instances = response.get('Reservations', [])
            selected_instance_id = instances[instance_number]['Instances'][0]['InstanceId']
            ec2.stop_instances(InstanceIds=[selected_instance_id])
            list_running_instances()
            success_label.config(text=f"Instance {selected_instance_id} stopped successfully!", fg="green")
        except (ValueError, IndexError) as e:
            success_label.config(text=str(e), fg="red")

    # Function to terminate instance
    def terminate_instance():
        try:
            instance_number = int(terminate_instance_entry.get()) - 1
            if instance_number < 0:
                raise ValueError("Instance number should be a positive integer.")
            response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
            instances = response.get('Reservations', [])
            selected_instance_id = instances[instance_number]['Instances'][0]['InstanceId']
            ec2.terminate_instances(InstanceIds=[selected_instance_id])
            list_running_instances()
            success_label.config(text=f"Instance {selected_instance_id} terminated successfully!", fg="green")
        except (ValueError, IndexError) as e:
            success_label.config(text=str(e), fg="red")

    # Labels and Entry widgets for instance management
    instance_count_label = tk.Label(instances_window, text="No. of Instances to Launch:")
    instance_count_label.grid(row=0, column=0, padx=10, pady=5)
    instance_count_entry = tk.Entry(instances_window)
    instance_count_entry.grid(row=0, column=1, padx=10, pady=5)

    launch_button = tk.Button(instances_window, text="Launch Instances", command=launch_instance)
    launch_button.grid(row=0, column=2, padx=10, pady=5)

    stop_instance_label = tk.Label(instances_window, text="Enter Instance Number to Stop:")
    stop_instance_label.grid(row=1, column=0, padx=10, pady=5)
    stop_instance_entry = tk.Entry(instances_window)
    stop_instance_entry.grid(row=1, column=1, padx=10, pady=5)

    stop_button = tk.Button(instances_window, text="Stop Instance", command=stop_instances)
    stop_button.grid(row=1, column=2, padx=10, pady=5)

    terminate_instance_label = tk.Label(instances_window, text="Enter Instance Number to Terminate:")
    terminate_instance_label.grid(row=2, column=0, padx=10, pady=5)
    terminate_instance_entry = tk.Entry(instances_window)
    terminate_instance_entry.grid(row=2, column=1, padx=10, pady=5)

    terminate_button = tk.Button(instances_window, text="Terminate Instance", command=terminate_instance)
    terminate_button.grid(row=2, column=2, padx=10, pady=5)

    instances_text = tk.Text(instances_window, width=50, height=10, state=tk.DISABLED)
    instances_text.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

    success_label = tk.Label(instances_window, text="", fg="green")
    success_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    list_running_instances()

def run_computer_vision():
    cap = cv2.VideoCapture(0)

    while True:
        status, photo = cap.read()

        cv2.namedWindow('Window 1', cv2.WINDOW_NORMAL)
        cv2.imshow('Window 1', photo)

        # Apply color effect by swapping red and blue channels
        color_effect_photo = photo[:, :, ::-1]  # Swap the red and blue channels

        cv2.namedWindow('Window 2', cv2.WINDOW_NORMAL)
        cv2.imshow('Window 2', color_effect_photo)

        if cv2.waitKey(30) == 13:  # Break the loop if Enter key is pressed
            break

    cv2.destroyAllWindows()
    cap.release()
    
    
def get_coordinates(location_name, coordinates_label):
    nom = ArcGIS()
    location = nom.geocode(location_name)
    if location:
        coordinates_label.config(text=f"Latitude: {location.latitude}, Longitude: {location.longitude}", fg="green")
    else:
        coordinates_label.config(text="Location not found", fg="red")

def open_location_window():
    location_window = tk.Toplevel()
    location_window.title("Enter Location")

    location_label = tk.Label(location_window, text="Enter name of location:")
    location_label.grid(row=0, column=0, padx=10, pady=5)

    location_entry = tk.Entry(location_window)
    location_entry.grid(row=0, column=1, padx=10, pady=5)

    coordinates_label = tk.Label(location_window, text="")
    coordinates_label.grid(row=1, column=0, columnspan=2)

    submit_button = tk.Button(location_window, text="Submit", command=lambda: get_coordinates(location_entry.get(), coordinates_label))
    submit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)



def send_email_window():
    email_window = tk.Toplevel()
    email_window.title("Send Email")

    sender_label = tk.Label(email_window, text="Sender Email ID:")
    sender_label.grid(row=0, column=0, padx=10, pady=5)
    sender_entry = tk.Entry(email_window)
    sender_entry.grid(row=0, column=1, padx=10, pady=5)

    password_label = tk.Label(email_window, text="Password:")
    password_label.grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(email_window, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=5)

    receiver_label = tk.Label(email_window, text="Receiver Email ID:")
    receiver_label.grid(row=2, column=0, padx=10, pady=5)
    receiver_entry = tk.Entry(email_window)
    receiver_entry.grid(row=2, column=1, padx=10, pady=5)

    title_label = tk.Label(email_window, text="Title:")
    title_label.grid(row=3, column=0, padx=10, pady=5)
    title_entry = tk.Entry(email_window)
    title_entry.grid(row=3, column=1, padx=10, pady=5)

    body_label = tk.Label(email_window, text="Message Body:")
    body_label.grid(row=4, column=0, padx=10, pady=5)
    body_entry = tk.Text(email_window, width=30, height=10)
    body_entry.grid(row=4, column=1, padx=10, pady=5)

    status_label = tk.Label(email_window, text="")
    status_label.grid(row=5, column=0, columnspan=2)

    send_button = tk.Button(email_window, text="Send Email", command=lambda: send_email(sender_entry.get(), password_entry.get(), receiver_entry.get(), title_entry.get(), body_entry.get(1.0, tk.END), status_label))
    send_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

def send_email(sender_email, password, receiver_email, title, body, status_label):
    try:
        pywhatkit.send_mail(sender_email, password, title, body, receiver_email)
        status_label.config(text="Email sent successfully!", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", fg="red")
def open_window(topic):
    if topic.lower() == "location":
        open_location_window()
    elif topic.lower() == "email":
        send_email_window()
    elif topic.lower() == "computer vision":
        run_computer_vision()
    elif topic.lower() == "instances":
        open_instances_window()

def open_s3_window():
    s3_window = tk.Toplevel()
    s3_window.title("S3 Management")

    # AWS region
    region_name = 'ap-south-1'

    # Create an S3 client
    s3 = boto3.client('s3', region_name=region_name)

    # Upload a file to S3 bucket
    def upload_file():
        try:
            bucket_name = bucket_entry.get()
            file_name = file_entry.get()
            object_name = object_entry.get()
            if not object_name:
                object_name = file_name
            response = s3.upload_file(file_name, bucket_name, object_name)
            status_label.config(text=f"{file_name} uploaded successfully to {bucket_name}/{object_name}", fg="green")
        except Exception as e:
            status_label.config(text=f"Upload failed: {e}", fg="red")

    # Delete a file from S3 bucket
    def delete_file():
        try:
            bucket_name = bucket_entry.get()
            object_name = object_entry.get()
            response = s3.delete_object(Bucket=bucket_name, Key=object_name)
            status_label.config(text=f"{object_name} deleted successfully from {bucket_name}", fg="green")
        except Exception as e:
            status_label.config(text=f"Delete failed: {e}", fg="red")

    # Labels and Entry widgets for S3 management
    bucket_label = tk.Label(s3_window, text="Bucket Name:")
    bucket_label.grid(row=0, column=0, padx=10, pady=5)
    bucket_entry = tk.Entry(s3_window)
    bucket_entry.grid(row=0, column=1, padx=10, pady=5)

    file_label = tk.Label(s3_window, text="File Name:")
    file_label.grid(row=1, column=0, padx=10, pady=5)
    file_entry = tk.Entry(s3_window)
    file_entry.grid(row=1, column=1, padx=10, pady=5)

    object_label = tk.Label(s3_window, text="Delete File Name (optional):")
    object_label.grid(row=2, column=0, padx=10, pady=5)
    object_entry = tk.Entry(s3_window)
    object_entry.grid(row=2, column=1, padx=10, pady=5)

    upload_button = tk.Button(s3_window, text="Upload File", command=upload_file)
    upload_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    delete_button = tk.Button(s3_window, text="Delete File", command=delete_file)
    delete_button.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    status_label = tk.Label(s3_window, text="", fg="green")
    status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        
def open_containerization_window():
      webbrowser.open("http://13.232.8.78:10001/")
    

def open_window(topic):
    if topic.lower() == "location":
        open_location_window()
    elif topic.lower() == "email":
        send_email_window()
    elif topic.lower() == "computer vision":
        run_computer_vision()
    elif topic.lower() == "instances":
        open_instances_window()
    elif topic.lower() == "s3":
        open_s3_window()
    elif topic.lower() == "containerization":
        open_containerization_window()
    elif topic.lower() == "genai":  # Add this block for GenAI
        open_genai_window()
def create_button(root, text, row, column):
    button = tk.Button(root, text=text, command=lambda: open_window(text))
    button.grid(row=row, column=column, padx=10, pady=10)

def main():
    root = tk.Tk()
    root.title("TEAM COIN")

    topics = [
        "Computer Vision",
        "Instances",
        "Email",
        "Location",
        "S3",
        "Containerization",
        "GenAI"
    ]

    for i, topic in enumerate(topics):
        row = i // 2
        column = i % 2
        create_button(root, topic, row, column)

    root.mainloop()

if __name__ == "__main__":
    main()

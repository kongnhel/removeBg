import os
import requests
import base64 # បន្ថែម​បណ្ណាល័យ base64
from flask import Flask, render_template, request, jsonify # ផ្លាស់ប្តូរ send_file ទៅ jsonify
from io import BytesIO

app = Flask(__name__)

# **********************************************
# កែសម្រួល​ព័ត៌មាន API ទាំងនេះ​ឱ្យ​ត្រូវ​ជាមួយ​សេវា​របស់​អ្នក
# **********************************************
# ចំណាំ៖ កូនសោ API របស់​អ្នក (tE6DfR1Ev7yYJjpgahuDvVfU) ត្រូវ​បាន​ដាក់​ឱ្យ​ដំណើរការ​ក្នុង​កូដ​នេះ
API_ENDPOINT = "https://api.remove.bg/v1.0/removebg"
# API_ENDPOINT = "https://api.remove.bg/v1.0/removebg"
API_KEY = "tE6DfR1Ev7yYJjpgahuDvVfU"

@app.route('/')
def index():
    """បង្ហាញ​ទំព័រ​ផ្ទុក​រូបភាព"""
    return render_template('index.html')

@app.route('/remove-background', methods=['POST'])
def remove_background_via_api():
    """ដំណើរការ​ដក​ផ្ទៃ​ខាង​ក្រោយ​ដោយ​ប្រើ API និង​ផ្ញើ​លទ្ធផល​ជា JSON"""
    if 'file' not in request.files:
        # ប្រើ jsonify ពេល​ប្រើ AJAX
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    # បង្កើត Headers សម្រាប់​ការ​ផ្ទៀងផ្ទាត់ (Authentication)
    headers = {
        'X-Api-Key': API_KEY, 
    }
    
    # បង្កើត Parameters សម្រាប់​ API (បញ្ជាក់​ថា​ចង់​បាន​រូបភាព​ PNG ថ្លា)
    # remove.bg ត្រូវការ​ការ​កំណត់​បន្ថែម​នេះ។
    data = {
        'size': 'auto',
        'response_format': 'png' # ធានា​ថា​ទទួល​បាន PNG ថ្លា
    }

    # បង្កើត Payload សម្រាប់​ផ្ញើ​ឯកសារ (Files)
    files = {'image_file': (file.filename, file.read(), file.content_type)}
    
    try:
        # ១. ផ្ញើ​សំណើ POST ទៅកាន់ API
        response = requests.post(API_ENDPOINT, headers=headers, files=files, data=data)
        
        # ២. ពិនិត្យ​មើល​ថា​សំណើ​ទទួល​បាន​ជោគជ័យ
        if response.status_code == 200:
            # ៣. ទទួល​រូបភាព​លទ្ធផល​ជា​ទិន្នន័យ (bytes)
            output_image_data = response.content
            
            # ៤. Base64 Encode រូបភាព​លទ្ធផល
            # នេះ​គឺ​ជា​គន្លឹះ​ដើម្បី​បង្ហាញ preview ក្នុង​ Browser ដោយ​មិន​ចាំបាច់​ទាញ​យក
            base64_encoded_image = base64.b64encode(output_image_data).decode('utf-8')
            
            # ៥. ផ្ញើ​ទិន្នន័យ JSON ត្រឡប់​ទៅ JavaScript
            return jsonify({
                'success': True,
                # បង្កើត Data URI
                'image_base64_png': f"data:image/png;base64,{base64_encoded_image}",
                'filename': f"api_removed_bg_{file.filename.split('.')[0]}.png"
            })
            
        else:
            # បង្ហាញ​កំហុស​ពី API
            return jsonify({'success': False, 'error': f"API Error: {response.status_code} - {response.text}"}), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f"Network Error: Could not connect to API. {e}"}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
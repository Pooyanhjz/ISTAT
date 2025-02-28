from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_session import Session  # Import Flask-Session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Flask-Session to use filesystem (store session data on the server)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = './flask_session/'
Session(app)  # Initialize the Flask-Session extension

# Global variable to store the processed DataFrame
df = None
concatenated_df = pd.DataFrame()  # Empty DataFrame for concatenation

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    if request.method == 'POST':
        file = request.files['file']
        
        # Check if the file is a CSV
        if file.filename.endswith('.csv'):
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file)
            
            # 1. Fill empty values of "statoEsteroStudioLavoro" with "Italia"
            if "statoEsteroStudioLavoro" in df.columns:
                df["statoEsteroStudioLavoro"] = df["statoEsteroStudioLavoro"].fillna("Italia")
            
            # 2. Add a new column "nome_di_mezzo" based on the "mezzo" column
            if "mezzo" in df.columns:
                mezzo_mapping = {
                    1: "treno",
                    2: "tram",
                    3: "metropolitana",
                    4: "autobus urbano, filobus",
                    5: "corriera, autobus extra-urbano",
                    6: "autobus aziendale o scolastico",
                    7: "auto privata (come conducente)",
                    8: "auto privata (come passeggero)",
                    9: "motocicletta, ciclomotore, scooter",
                    10: "bicicletta",
                    11: "altro mezzo",
                    12: "a piedi"
                }
                df["nome_di_mezzo"] = df["mezzo"].map(mezzo_mapping)
            
            # 3. Add a new column "nome_di_motivo_spostamento" based on the "motivoSpostamento" column
            if "motivoSpostamento" in df.columns:
                motivo_mapping = {
                    1: "si reca al luogo di studio",
                    2: "si reca al luogo di lavoro"
                }
                df["nome_di_motivo_spostamento"] = df["motivoSpostamento"].map(motivo_mapping)
            
            # Get unique regioni_res options
            regioni_res = df['regioneResidenza'].unique().tolist()
            
            return render_template('index.html', regioni_res=regioni_res)
        
        else:
            return 'Please upload a CSV file', 400
    
    return render_template('index.html')

@app.route('/provinces', methods=['POST'])
def provinces():
    global df
    if df is not None:
        selected_regioni_res = request.form.getlist('regioni_res')
        session['selected_regioni_res'] = selected_regioni_res  # Store in session
        province_res = df[df['regioneResidenza'].isin(selected_regioni_res)]['provinciaResidenza'].unique().tolist()
        
        return render_template('provinces.html', province_res=province_res, selected_regioni_res=selected_regioni_res)
    
    return redirect(url_for('index'))

@app.route('/comuni', methods=['POST'])
def comuni():
    global df
    if df is not None:
        # Get selected province_res as a list
        selected_province_res = request.form.getlist('province_res[]')
        
        # Store the selected province_res in session
        session['selected_province_res'] = selected_province_res
        
        # Debugging: Print the session values
        print("Selected Province Res:", selected_province_res)
        print("Session Value:", session.get('selected_province_res'))

        comuni_res = df[df['provinciaResidenza'].isin(selected_province_res)]['comuneResidenza'].unique().tolist()

        return render_template('comuni.html', comuni_res=comuni_res, selected_province_res=selected_province_res)
    
    return redirect(url_for('index'))




@app.route('/regioni_sl', methods=['POST'])
def regioni_sl():
    global df
    if df is not None:
        # Check if comuni_res is in the form data
        selected_comuni_res = request.form.getlist('comuni_res[]')
        
        # Only store it in session if it's not empty
        if selected_comuni_res:
            session['selected_comuni_res'] = selected_comuni_res
        print("Selected Province Res:", selected_comuni_res)
        print("Session Value:", session.get('selected_comuni_res'))

        regioni_sl = df['regioneSL'].unique().tolist()
        return render_template('regioni_sl.html', regioni_sl=regioni_sl)
    
    return redirect(url_for('index'))

@app.route('/provinces_sl', methods=['POST'])
def provinces_sl():
    global df
    if df is not None:
        selected_regioni_sl = request.form.getlist('regioni_sl')
        session['selected_regioni_sl'] = selected_regioni_sl
        province_sl = df[df['regioneSL'].isin(selected_regioni_sl)]['provinciaSL'].unique().tolist()
        
        return render_template('provinces_sl.html', province_sl=province_sl, selected_regioni_sl=selected_regioni_sl)
    
    return redirect(url_for('regioni_sl'))

@app.route('/comuni_sl', methods=['POST'])
def comuni_sl():
    global df
    if df is not None:
        selected_province_sl = request.form.getlist('province_sl[]')
        session['selected_province_sl'] = selected_province_sl
        comuni_sl = df[df['provinciaSL'].isin(selected_province_sl)]['comuneSL'].unique().tolist()
        
        return render_template('comuni_sl.html', comuni_sl=comuni_sl, selected_province_sl=selected_province_sl)
    
    return redirect(url_for('regioni_sl'))

@app.route('/transport', methods=['POST'])
def transport():
    # Check if comuni_res is in the form data
    selected_comuni_sl = request.form.getlist('comuni_sl[]')
        
    # Only store it in session if it's not empty
    if selected_comuni_sl:
        session['selected_comuni_sl'] = selected_comuni_sl
    print("Selected comuni sl:", selected_comuni_sl)
    print("Session Value:", session.get('selected_comuni_sl'))
    transport_options = [
        "1 treno", "2 tram", "3 metropolitana", "4 autobus urbano, filobus",
        "5 corriera, autobus extra-urbano", "6 autobus aziendale o scolastico",
        "7 auto privata (come conducente)", "8 auto privata (come passeggero)",
        "9 motocicletta, ciclomotore, scooter", "10 bicicletta", "11 altro mezzo", "12 a piedi"
    ]
    return render_template('transport.html', transport_options=transport_options)

@app.route('/reason', methods=['POST'])
def reason():
    # Check if comuni_res is in the form data
    selected_transport = request.form.getlist('transport_options[]')
        
    # Only store it in session if it's not empty
    if selected_transport:
        session['transport_options'] = selected_transport
    reason_options = [
        "1 si reca al luogo di studio", 
        "2 si reca al luogo di lavoro"
    ]
    return render_template('reason.html', reason_options=reason_options)

@app.route('/country', methods=['POST'])
def country():
    global df
    if df is not None:
            # Check if comuni_res is in the form data
        selected_reason = request.form.getlist('reason_options')
        
    # Only store it in session if it's not empty
        if selected_reason:
            session['reason_options'] = selected_reason
        country = df["statoEsteroStudioLavoro"].unique().tolist()
        return render_template('country.html', country=country)
    
    return redirect(url_for('index'))

# Continue Filtering Route
@app.route('/continue_filtering', methods=['GET', 'POST'])
def continue_filtering():
    if request.method == 'POST':
        # Get the user's choice from the form
        choice = request.form.get('choice')
        
        if choice == 'yes':
            # If yes, restart the filtering process from the start
            return redirect(url_for('index'))
        else:
            # If no, render the result.html directly with download link
            return render_template('result.html', 
                                   download_link=url_for('download_file'))
    
    # Render the confirmation page
    return render_template('continue_filtering.html')




@app.route('/result', methods=['POST'])
def result():
    global df, concatenated_df  # Use the global concatenated_df
    selected_country = request.form.getlist('country')
        
    # Only store it in session if it's not empty
    if selected_country:
        session['selected_country'] = selected_country
    
    if df is not None:
        selected_regioni_res = session.get('selected_regioni_res', [])
        selected_province_res = session.get('selected_province_res', [])
        selected_comuni_res = session.get('selected_comuni_res', [])
        selected_regioni_sl = session.get('selected_regioni_sl', [])
        selected_province_sl = session.get('selected_province_sl', [])
        selected_comuni_sl = session.get('selected_comuni_sl', [])
        selected_transport = session.get('transport_options', [])
        selected_reason = session.get('reason_options', [])
        selected_country = session.get('selected_country', [])  # Use session instead of request.form
        
        # Debugging: Print all session values
        print("Session Values:")
        print("selected_regioni_res:", selected_regioni_res)
        print("selected_province_res:", selected_province_res)
        print("selected_comuni_res:", selected_comuni_res)
        print("selected_regioni_sl:", selected_regioni_sl)
        print("selected_province_sl:", selected_province_sl)
        print("selected_comuni_sl:", selected_comuni_sl)
        print("selected_transport:", selected_transport)
        print("selected_reason:", selected_reason)
        print("selected_country:", selected_country)
        
        # Apply the filters to the DataFrame
        filtered_df = df[
            df['regioneResidenza'].isin(selected_regioni_res) &
            df['provinciaResidenza'].isin(selected_province_res) &
            df['comuneResidenza'].isin(selected_comuni_res) &
            df['regioneSL'].isin(selected_regioni_sl) &
            df['provinciaSL'].isin(selected_province_sl) &
            df['comuneSL'].isin(selected_comuni_sl) &
            df['mezzo'].isin([int(t.split()[0]) for t in selected_transport]) &
            df['motivoSpostamento'].isin([int(r.split()[0]) for r in selected_reason]) &
            df["statoEsteroStudioLavoro"].isin(selected_country)
        ]
        # Debugging: Print each condition separately
        print("\nDebugging Filter Conditions:-------------------------------------------------------------------------------------")

        regioni_res_filter = df['regioneResidenza'].isin(selected_regioni_res)
        print("regioneResidenza Filter:")
        print(regioni_res_filter.value_counts())

        province_res_filter = df['provinciaResidenza'].isin(selected_province_res)
        print("\nprovinciaResidenza Filter:")
        print(province_res_filter.value_counts())

        comuni_res_filter = df['comuneResidenza'].isin(selected_comuni_res)
        print("\ncomuneResidenza Filter:")
        print(comuni_res_filter.value_counts())

        regioni_sl_filter = df['regioneSL'].isin(selected_regioni_sl)
        print("\nregioneSL Filter:")
        print(regioni_sl_filter.value_counts())

        province_sl_filter = df['provinciaSL'].isin(selected_province_sl)
        print("\nprovinciaSL Filter:")
        print(province_sl_filter.value_counts())

        comuni_sl_filter = df['comuneSL'].isin(selected_comuni_sl)
        print("\ncomuneSL Filter:")
        print(comuni_sl_filter.value_counts())

        transport_filter = df['mezzo'].isin([int(t.split()[0]) for t in selected_transport])
        print("\nmezzo (Transport) Filter:")
        print(transport_filter.value_counts())

        reason_filter = df['motivoSpostamento'].isin([int(r.split()[0]) for r in selected_reason])
        print("\nmotivoSpostamento (Reason) Filter:")
        print(reason_filter.value_counts())

        country_filter = df["statoEsteroStudioLavoro"].isin(selected_country)
        print("\nstatoEsteroStudioLavoro (Country) Filter:")
        print(country_filter.value_counts())
        print(filtered_df)

        # Path to the filtered file
        filtered_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'filtered_data.csv')

        # Concatenate the new filtered data to the existing concatenated_df
        concatenated_df = pd.concat([concatenated_df, filtered_df], ignore_index=True)

        # Save the concatenated DataFrame to the file
        concatenated_df.to_csv(filtered_file_path, index=False)

        # Store the current selection as a history in session
        # Initialize history lists if they don't exist
        if 'history_regioni_res' not in session:
            session['history_regioni_res'] = []
        if 'history_province_res' not in session:
            session['history_province_res'] = []
        if 'history_comuni_res' not in session:
            session['history_comuni_res'] = []
        if 'history_regioni_sl' not in session:
            session['history_regioni_sl'] = []
        if 'history_province_sl' not in session:
            session['history_province_sl'] = []
        if 'history_comuni_sl' not in session:
            session['history_comuni_sl'] = []
        if 'history_transport' not in session:
            session['history_transport'] = []
        if 'history_reason' not in session:
            session['history_reason'] = []
        if 'history_country' not in session:
            session['history_country'] = []

        # Append the current selection to the history lists
        session['history_regioni_res'].append(selected_regioni_res)
        session['history_province_res'].append(selected_province_res)
        session['history_comuni_res'].append(selected_comuni_res)
        session['history_regioni_sl'].append(selected_regioni_sl)
        session['history_province_sl'].append(selected_province_sl)
        session['history_comuni_sl'].append(selected_comuni_sl)
        session['history_transport'].append(selected_transport)
        session['history_reason'].append(selected_reason)
        session['history_country'].append(selected_country)

        # Redirect to the /continue_filtering route to ask user if they want to filter again
        return redirect(url_for('continue_filtering'))

    # Redirect to the main page if df is not loaded
    return redirect(url_for('index'))


# Download Route
@app.route('/download')
def download_file():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'filtered_data.csv')
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "<h3>No file available for download. Please apply filters first.</h3>"

if __name__ == '__main__':
    app.run(debug=True)


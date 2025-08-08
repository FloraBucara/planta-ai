import streamlit as st

def aplicar_estilos():
    """Aplica todos los estilos CSS de la aplicación"""
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 1rem 0;
            background: linear-gradient(90deg, #2E8B57, #98FB98);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .prediction-card {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #28a745;
            margin: 1rem 0;
        }
        
        .info-card {
            background: #e8f5e9;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .species-card {
            background: #f0f8ff;
            padding: 1rem;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            margin: 0.5rem 0;
            text-align: center;
            transition: all 0.3s;
        }
        
        .species-card:hover {
            border-color: #28a745;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .debug-info {
            background: #fff3cd;
            color: #856404;
            padding: 0.75rem;
            border-radius: 5px;
            border: 1px solid #ffeaa7;
            margin: 0.5rem 0;
            font-size: 0.9em;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid #f5c6cb;
            margin: 1rem 0;
        }
        
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            border: 1px solid #c3e6cb;
            margin: 1rem 0;
        }
        
        .firestore-status {
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
        }
        
        .firestore-connected {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .firestore-disconnected {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        
        .confidence-bar {
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            margin: 0.5rem 0;
            overflow: hidden;
        }
        
        .confidence-fill {
            background: linear-gradient(90deg, #28a745, #20c997);
            height: 100%;
            transition: width 0.3s ease;
        }
        
        .camera-info {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
            margin: 1rem 0;
        }
        
        .upload-info {
            background: #f3e5f5;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
            margin: 1rem 0;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
            border-radius: 8px 8px 0 0;
        }
    </style>
    """, unsafe_allow_html=True)
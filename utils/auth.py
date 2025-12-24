import streamlit as st
from utils.database import register_user, verify_user, user_exists, email_exists
import re

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_username(username):
    """Validate username format"""
    # Username should be 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def is_valid_password(password):
    """Validate password strength"""
    # At least 6 characters
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def show_login_page():
    """Display login page"""
    st.markdown('<div class="main-header">Login</div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                success, result = verify_user(username, password)
                if success:
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = result
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result)
    
    st.markdown("---")
    st.markdown("Don't have an account? Register below.")
    
    if st.button("Go to Register", use_container_width=True):
        st.session_state['page'] = 'register'
        st.rerun()

def show_register_page():
    """Display registration page"""
    st.markdown('<div class="main-header">Register</div>', unsafe_allow_html=True)
    
    with st.form("register_form"):
        username = st.text_input("Username", placeholder="Choose a username (3-20 characters)")
        email = st.text_input("Email", placeholder="Enter your email address")
        password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        submit = st.form_submit_button("Register", type="primary", use_container_width=True)
        
        if submit:
            # Validation
            errors = []
            
            if not username or not email or not password or not confirm_password:
                errors.append("Please fill in all fields.")
            else:
                if not is_valid_username(username):
                    errors.append("Username must be 3-20 characters and contain only letters, numbers, and underscores.")
                
                if not is_valid_email(email):
                    errors.append("Please enter a valid email address.")
                
                valid_pass, pass_error = is_valid_password(password)
                if not valid_pass:
                    errors.append(pass_error)
                
                if password != confirm_password:
                    errors.append("Passwords do not match.")
                
                if user_exists(username):
                    errors.append("Username already exists. Please choose another.")
                
                if email_exists(email):
                    errors.append("Email already registered. Please use another email.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                    st.info("You can now login with your credentials.")
                    # Set flag to redirect to login after form submission
                    st.session_state['redirect_to_login'] = True
                else:
                    st.error(message)
    
    # Check if we should redirect to login after successful registration
    if st.session_state.get('redirect_to_login', False):
        st.session_state['redirect_to_login'] = False
        st.session_state['page'] = 'login'
        st.rerun()
    
    st.markdown("---")
    st.markdown("Already have an account? Login below.")
    
    if st.button("Go to Login", use_container_width=True):
        st.session_state['page'] = 'login'
        st.rerun()

def logout():
    """Logout user"""
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    if 'user' in st.session_state:
        del st.session_state['user']
    st.session_state['page'] = 'login'
    st.rerun()

def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    
    if not st.session_state['authenticated']:
        if st.session_state['page'] == 'register':
            show_register_page()
        else:
            show_login_page()
        return False
    
    return True


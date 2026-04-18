import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Virtual Lithography Lab", layout="wide")

# -------------------------------
# CONSTANTS
# -------------------------------
RESIST_CONSTANTS = {"AZ 1505": 31.62}

# -------------------------------
# SESSION STATE
# -------------------------------
if 'current_thickness' not in st.session_state:
    st.session_state.current_thickness = 0.0
if 'selected_resist' not in st.session_state:
    st.session_state.selected_resist = "AZ 1505"
if 'resist_status' not in st.session_state:
    st.session_state.resist_status = "Unbaked"

# -------------------------------
# 3D BLOCK FUNCTION
# -------------------------------
def create_block(x0, y0, dx, dy, z0, dz, color, opacity=1.0):
    x = [x0, x0+dx, x0+dx, x0, x0, x0+dx, x0+dx, x0]
    y = [y0, y0, y0+dy, y0+dy, y0, y0, y0+dy, y0+dy]
    z = [z0, z0, z0, z0, z0+dz, z0+dz, z0+dz, z0+dz]

    i = [0,0,0,1,1,2,4,4,5,6,3,2]
    j = [1,2,3,2,5,3,5,6,6,7,7,6]
    k = [2,3,1,5,6,7,6,7,4,4,4,7]

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        flatshading=True
    )

# -------------------------------
# MASK FUNCTION
# -------------------------------
def generate_mask(size, pattern):
    mask = np.zeros((size, size))

    if pattern == "Lines":
        mask[:, ::4] = 1
    elif pattern == "Dots":
        for i in range(0, size, 6):
            for j in range(0, size, 6):
                mask[i:i+2, j:j+2] = 1
    elif pattern == "Square":
        mask[10:20, 10:20] = 1

    return mask

# -------------------------------
# MAIN UI
# -------------------------------
st.title("🔬 Virtual Lab: Photolithography Process")
st.markdown("Explore the deposition and baking of positive photoresists on a silicon substrate.")

tab_aim, tab_theory, tab_procedure, tab_simulation, tab_quiz = st.tabs([
    "🎯 Aim", "📚 Theory", "📝 Procedure", "⚙️ Simulation", "🧠 Quiz"
])

# -------------------------------
# AIM
# -------------------------------
with tab_aim:
    st.header("Objective")
    st.markdown("""
    * Understand spin coating and thickness relation  
    * Study soft bake effects  
    * Visualize lithography in 3D  
    """)

# -------------------------------
# THEORY
# -------------------------------
with tab_theory:
    st.header("Theory")
    st.markdown("""
    Thickness follows:

    t = k / √RPM

    Soft bake removes solvent and stabilizes resist.
    """)

# -------------------------------
# PROCEDURE
# -------------------------------
with tab_procedure:
    st.header("Procedure")
    st.markdown("""
    1. Spin coat  
    2. Bake  
    3. Expose  
    4. Develop  
    """)

# -------------------------------
# 🔥 SIMULATION (UPDATED TO 3D)
# -------------------------------
with tab_simulation:

    st.header("3D Lithography Simulation")

    st.sidebar.title("Lab Controls")

    rpm = st.sidebar.slider("Spin Speed (RPM)", 500, 5000, 3000)

    k_val = RESIST_CONSTANTS["AZ 1505"]
    thickness_um = k_val / np.sqrt(rpm)

    st.session_state.current_thickness = thickness_um

    st.sidebar.markdown(f"**Thickness:** {thickness_um:.3f} µm")

    step = st.sidebar.radio(
        "Select Step",
        ["1. Spin Coating", "2. Layer Stack", "3. Exposure", "4. Development"]
    )

    size = 12
    dx = 1 / size

    substrate_h = 200
    sio2_h = 200
    resist_h = thickness_um * 100

    # STEP 1
    if step == "1. Spin Coating":
        fig = go.Figure()
        fig.add_trace(create_block(0,0,1,1,0,substrate_h,"gray"))
        fig.add_trace(create_block(0,0,1,1,substrate_h,sio2_h,"blue"))
        fig.add_trace(create_block(0,0,1,1,substrate_h+sio2_h,resist_h,"orange"))

        st.plotly_chart(fig, use_container_width=True)

    # STEP 2
    elif step == "2. Layer Stack":
        fig = go.Figure()
        fig.add_trace(create_block(0,0,1,1,0,substrate_h,"gray"))
        fig.add_trace(create_block(0,0,1,1,substrate_h,sio2_h,"blue"))
        fig.add_trace(create_block(0,0,1,1,substrate_h+sio2_h,resist_h,"orange"))

        st.plotly_chart(fig, use_container_width=True)

    # STEP 3
    elif step == "3. Exposure":
        pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
        mask = generate_mask(size, pattern)

        fig = go.Figure()
        fig.add_trace(create_block(0,0,1,1,0,substrate_h,"gray"))
        fig.add_trace(create_block(0,0,1,1,substrate_h,sio2_h,"blue"))

        for i in range(size):
            for j in range(size):
                x0, y0 = i*dx, j*dx
                exposed = mask[i,j] == 1

                color = "red" if exposed else "orange"

                fig.add_trace(create_block(
                    x0, y0, dx, dx,
                    substrate_h + sio2_h,
                    resist_h,
                    color
                ))

                if exposed:
                    fig.add_trace(create_block(
                        x0, y0, dx, dx,
                        substrate_h + sio2_h + resist_h,
                        150,
                        "yellow",
                        opacity=0.2
                    ))

        st.plotly_chart(fig, use_container_width=True)

    # STEP 4
    elif step == "4. Development":
        pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
        mask = generate_mask(size, pattern)

        fig = go.Figure()
        fig.add_trace(create_block(0,0,1,1,0,substrate_h,"gray"))
        fig.add_trace(create_block(0,0,1,1,substrate_h,sio2_h,"blue"))

        for i in range(size):
            for j in range(size):
                if mask[i,j] == 0:
                    x0, y0 = i*dx, j*dx

                    fig.add_trace(create_block(
                        x0, y0, dx, dx,
                        substrate_h + sio2_h,
                        resist_h,
                        "green"
                    ))

        st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# QUIZ
# -------------------------------
with tab_quiz:
    st.header("Quiz")
    st.write("1. Why does thickness decrease with RPM?")

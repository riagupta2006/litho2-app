import streamlit as st
import numpy as np
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
# MASK
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
# RPM FUNCTION
# -------------------------------
def calculate_thickness(rpm):
    k = RESIST_CONSTANTS["AZ 1505"]
    return k / np.sqrt(rpm)

# -------------------------------
# MAIN UI
# -------------------------------
st.title("🔬 Virtual Lab: Photolithography Process")

tab_aim, tab_theory, tab_procedure, tab_simulation, tab_quiz = st.tabs([
    "🎯 Aim", "📚 Theory", "📝 Procedure", "⚙️ Simulation", "🧠 Quiz"
])

# -------------------------------
# AIM
# -------------------------------
with tab_aim:
    st.header("Objective")
    st.write("Understand spin coating, baking, and lithography patterning.")

# -------------------------------
# THEORY
# -------------------------------
with tab_theory:
    st.header("Theory")
    st.write("Thickness ∝ 1 / √RPM. Soft bake removes solvent.")

# -------------------------------
# PROCEDURE
# -------------------------------
with tab_procedure:
    st.header("Procedure")
    st.write("1. Spin coat\n2. Bake\n3. Expose\n4. Develop")

# -------------------------------
# 🔥 SIMULATION (REPLACED)
# -------------------------------
with tab_simulation:

    st.header("3D Lithography Simulation")

    size = 12
    dx = 1 / size

    # -------------------
    # STEP 1: SPIN COATING
    # -------------------
    st.subheader("Step 1: Spin Coating")

    rpm = st.slider("Spin Speed (RPM)", 500, 5000, 3000)
    thickness = calculate_thickness(rpm)
    st.session_state.current_thickness = thickness * 100  # scaled for 3D

    st.write(f"Thickness: **{thickness:.3f} µm**")

    # -------------------
    # STEP 2: STACK BUILD
    # -------------------
    st.subheader("Step 2: Layer Formation")

    sio2_thickness = 200
    resist_thickness = st.session_state.current_thickness

    fig2 = go.Figure()
    fig2.add_trace(create_block(0,0,1,1,0,200,"gray"))
    fig2.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))
    fig2.add_trace(create_block(0,0,1,1,200+sio2_thickness,resist_thickness,"orange"))

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------
    # STEP 3: EXPOSURE
    # -------------------
    st.subheader("Step 3: Exposure")

    pattern = st.selectbox("Mask Pattern", ["Lines", "Dots", "Square"])
    mask = generate_mask(size, pattern)

    fig3 = go.Figure()
    fig3.add_trace(create_block(0,0,1,1,0,200,"gray"))
    fig3.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

    for i in range(size):
        for j in range(size):
            x0, y0 = i*dx, j*dx
            exposed = mask[i,j] == 1

            color = "red" if exposed else "orange"

            fig3.add_trace(create_block(
                x0, y0, dx, dx,
                200 + sio2_thickness,
                resist_thickness,
                color
            ))

            if exposed:
                fig3.add_trace(create_block(
                    x0, y0, dx, dx,
                    200 + sio2_thickness + resist_thickness,
                    150,
                    "yellow",
                    opacity=0.2
                ))

    st.plotly_chart(fig3, use_container_width=True)

    # -------------------
    # STEP 4: DEVELOPMENT
    # -------------------
    st.subheader("Step 4: Development")

    fig4 = go.Figure()
    fig4.add_trace(create_block(0,0,1,1,0,200,"gray"))
    fig4.add_trace(create_block(0,0,1,1,200,sio2_thickness,"blue"))

    for i in range(size):
        for j in range(size):
            if mask[i,j] == 0:
                x0, y0 = i*dx, j*dx

                fig4.add_trace(create_block(
                    x0, y0, dx, dx,
                    200 + sio2_thickness,
                    resist_thickness,
                    "green"
                ))

    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# QUIZ
# -------------------------------
with tab_quiz:
    st.header("Quiz")
    st.write("1. Why does thickness decrease with RPM?")

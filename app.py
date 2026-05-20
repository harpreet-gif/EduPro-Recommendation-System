import streamlit as st
import pandas as pd

# Load data
learner_profile = pd.read_csv("clustered_learners.csv")
courses = pd.read_csv("data/courses.csv")
transactions = pd.read_csv("data/transactions.csv")
# Merge data
data = transactions.merge(courses, on='CourseID', how='left')

# Recommendation Function
def recommend_courses(user_id, top_n=5):
    
    user_cluster = learner_profile[
        learner_profile['UserID'] == user_id
    ]['cluster'].values[0]
    
    similar_users = learner_profile[
        learner_profile['cluster'] == user_cluster
    ]['UserID']
    
    cluster_data = data[data['UserID'].isin(similar_users)]
    
    user_courses = data[data['UserID'] == user_id]['CourseID']
    
    cluster_data = cluster_data[
        ~cluster_data['CourseID'].isin(user_courses)
    ]
    
    course_scores = cluster_data.groupby('CourseID').agg({
        'UserID': 'count',
        'CourseRating': 'mean'
    }).rename(columns={
        'UserID': 'popularity',
        'CourseRating': 'avg_rating'
    })
    
    course_scores['score'] = (
        course_scores['popularity'] * 0.6 +
        course_scores['avg_rating'] * 0.4
    )
    
    top_courses = course_scores.sort_values(
        by='score', ascending=False
    ).head(top_n)
    
    return courses[courses['CourseID'].isin(top_courses.index)]


# ---------------- UI ---------------- #

st.title("🎓 EduPro: Personalized Course Recommendation System")

# Select User
user_id = st.selectbox(
    "Select User ID",
    learner_profile['UserID']
)

# Show User Info
user_data = learner_profile[
    learner_profile['UserID'] == user_id
]

st.subheader("👤 Learner Profile")
st.write(user_data)

# Show Cluster
cluster = user_data['cluster'].values[0]
st.subheader(f"📊 Assigned Segment: {cluster}")

# Recommendation Button
if st.button("🚀 Get Recommendations"):
    
    recs = recommend_courses(user_id)
    
    st.subheader("📚 Recommended Courses")
    st.dataframe(recs)

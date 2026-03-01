#!/usr/bin/env python3
"""
Enhanced course catalog generation with hierarchical data.

Generates courses with full syllabi, assignments, learning objectives,
and prerequisites. Saves in both JSON and human-readable markdown format.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, List

import click
from faker import Faker
from ulid import ULID

from redis_context_course.hierarchical_models import (
    Assignment,
    AssignmentType,
    CourseDetails,
    CourseSummary,
    CourseSyllabus,
    HierarchicalCourse,
    WeekPlan,
)
from redis_context_course.models import (
    CourseFormat,
    DifficultyLevel,
    Prerequisite,
    Semester,
)

fake = Faker()


class HierarchicalCourseGenerator:
    """Generates rich course data with syllabi and assignments."""

    def __init__(self, seed: int = None):
        if seed:
            random.seed(seed)
            fake.seed_instance(seed)

        self.generated_courses: List[HierarchicalCourse] = []

    def generate_courses(self, count: int = 50) -> List[HierarchicalCourse]:
        """Generate hierarchical courses with full details.

        Creates one instance of each template, cycling through templates
        if count exceeds the number of templates.
        """

        # Course templates with rich content
        templates = self._get_course_templates()

        for i in range(count):
            # Cycle through templates instead of random selection
            template = templates[i % len(templates)]
            course = self._generate_course_from_template(template, i + 1)
            self.generated_courses.append(course)

        return self.generated_courses

    def _get_course_templates(self) -> List[Dict[str, Any]]:
        """Define rich course templates across diverse fields.

        Creates a comprehensive 50-course catalog with proper progression
        from beginner to advanced across multiple disciplines.
        """
        return [
            # ============================================================
            # COMPUTER SCIENCE (22 courses)
            # ============================================================

            # CS Fundamentals (Beginner)
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Introduction to Programming with Python",
                "short_desc": "Learn programming fundamentals using Python for beginners.",
                "full_desc": "Learn programming fundamentals using Python for beginners. This course introduces students to computational thinking, problem-solving, and programming basics. No prior experience required. Students will learn variables, control flow, functions, data structures, and object-oriented programming through hands-on projects and real-world examples.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["programming", "python", "beginner", "fundamentals", "intro"],
                "weeks": 14,
                "topics": [
                    "Introduction to Computing and Python",
                    "Variables, Types, and Expressions",
                    "Control Flow: Conditionals and Loops",
                    "Functions and Modularity",
                    "Lists and Tuples",
                    "Dictionaries and Sets",
                    "File Input/Output",
                    "Error Handling and Debugging",
                    "Introduction to OOP",
                    "Classes and Objects",
                    "Working with Libraries",
                    "Final Project Development",
                    "Final Project Presentations",
                    "Course Review",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Web Development Fundamentals",
                "short_desc": "Introduction to web programming with HTML, CSS, and JavaScript.",
                "full_desc": "Introduction to web programming with HTML, CSS, and JavaScript. This beginner-friendly course teaches students how to build interactive websites from scratch. No prior programming experience required. Students will learn HTML structure, CSS styling, JavaScript programming, responsive design, and modern web development practices through hands-on projects.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["programming", "web", "javascript", "html", "css", "beginner", "frontend"],
                "weeks": 14,
                "topics": [
                    "Introduction to Web Technologies",
                    "HTML Fundamentals and Structure",
                    "CSS Styling and Layout",
                    "Responsive Design Principles",
                    "JavaScript Basics",
                    "DOM Manipulation",
                    "Event Handling",
                    "Forms and Validation",
                    "Introduction to Frameworks",
                    "Web APIs and Fetch",
                    "Version Control with Git",
                    "Final Project Development",
                    "Final Project Presentations",
                    "Course Review",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Programming Fundamentals with C++",
                "short_desc": "Core programming concepts using C++ for beginners.",
                "full_desc": "Core programming concepts using C++ for beginners. This course introduces students to programming fundamentals using C++, focusing on computational thinking, problem-solving, and software development. No prior experience required. Students will learn variables, control structures, functions, arrays, pointers, object-oriented programming, and memory management through practical exercises.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["programming", "c++", "beginner", "fundamentals", "systems"],
                "weeks": 14,
                "topics": [
                    "Introduction to C++ and Compilation",
                    "Variables, Data Types, and Operators",
                    "Control Flow and Loops",
                    "Functions and Parameter Passing",
                    "Arrays and Strings",
                    "Pointers and References",
                    "Dynamic Memory Allocation",
                    "Introduction to OOP in C++",
                    "Classes and Objects",
                    "Constructors and Destructors",
                    "File I/O and Streams",
                    "Final Project Development",
                    "Final Project Presentations",
                    "Course Review",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Data Structures and Algorithms",
                "short_desc": "Essential data structures and algorithmic problem-solving.",
                "full_desc": "Essential data structures and algorithmic problem-solving. This course covers arrays, linked lists, stacks, queues, trees, graphs, and hash tables. Students will analyze algorithm complexity and implement efficient solutions to computational problems.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["algorithms", "data structures", "complexity", "problem solving"],
                "weeks": 15,
                "topics": [
                    "Algorithm Analysis and Big-O Notation",
                    "Arrays and Dynamic Arrays",
                    "Linked Lists",
                    "Stacks and Queues",
                    "Recursion",
                    "Trees and Binary Search Trees",
                    "Tree Traversals",
                    "Heaps and Priority Queues",
                    "Hash Tables",
                    "Graphs and Graph Representations",
                    "Graph Traversal: BFS and DFS",
                    "Sorting Algorithms",
                    "Dynamic Programming",
                    "Greedy Algorithms",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Database Systems",
                "short_desc": "Relational databases, SQL, and data modeling.",
                "full_desc": "Relational databases, SQL, and data modeling. This course covers database design, normalization, SQL programming, and transaction management. Students will design and implement databases for real-world applications.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["databases", "sql", "data modeling", "postgresql"],
                "weeks": 14,
                "topics": [
                    "Introduction to Database Systems",
                    "Relational Model and ER Diagrams",
                    "SQL Basics: SELECT, INSERT, UPDATE",
                    "Advanced SQL: JOINs and Subqueries",
                    "Database Normalization",
                    "Indexing and Query Optimization",
                    "Transactions and ACID Properties",
                    "Stored Procedures and Triggers",
                    "NoSQL Introduction",
                    "Database Security",
                    "Data Warehousing",
                    "Database Administration",
                    "Final Project",
                    "Final Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Web Development",
                "short_desc": "Full-stack web development with modern frameworks.",
                "full_desc": "Full-stack web development with modern frameworks. Students will build responsive web applications using HTML, CSS, JavaScript, React, and Node.js. Topics include REST APIs, authentication, and deployment.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["web development", "javascript", "react", "full stack"],
                "weeks": 14,
                "topics": [
                    "HTML and CSS Fundamentals",
                    "JavaScript Basics",
                    "DOM Manipulation",
                    "Responsive Design",
                    "Introduction to React",
                    "React Components and State",
                    "React Hooks",
                    "Node.js and Express",
                    "REST API Design",
                    "Authentication and Authorization",
                    "Database Integration",
                    "Deployment and DevOps",
                    "Final Project Development",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Software Engineering",
                "short_desc": "Software development lifecycle, design patterns, and best practices.",
                "full_desc": "Software development lifecycle, design patterns, and best practices. This course covers requirements analysis, system design, testing, and maintenance. Students will work in teams to build a substantial software project using agile methodologies.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["software engineering", "design patterns", "agile", "testing"],
                "weeks": 14,
                "topics": [
                    "Software Development Lifecycle",
                    "Requirements Engineering",
                    "System Design and Architecture",
                    "Design Patterns: Creational",
                    "Design Patterns: Structural",
                    "Design Patterns: Behavioral",
                    "Version Control with Git",
                    "Testing: Unit and Integration",
                    "Test-Driven Development",
                    "Agile and Scrum",
                    "Code Review and Quality",
                    "CI/CD Pipelines",
                    "Team Project Sprint",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Operating Systems",
                "short_desc": "Process management, memory, file systems, and concurrency.",
                "full_desc": "Process management, memory, file systems, and concurrency. This course explores how operating systems manage hardware resources and provide services to applications. Topics include scheduling, virtual memory, and synchronization.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["operating systems", "processes", "memory", "concurrency"],
                "weeks": 15,
                "topics": [
                    "Introduction to Operating Systems",
                    "Processes and Threads",
                    "CPU Scheduling",
                    "Process Synchronization",
                    "Deadlocks",
                    "Memory Management",
                    "Virtual Memory",
                    "Paging and Segmentation",
                    "File Systems",
                    "I/O Systems",
                    "Disk Scheduling",
                    "Protection and Security",
                    "Distributed Systems",
                    "Case Studies: Linux and Windows",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Computer Networks",
                "short_desc": "Network protocols, architecture, and internet technologies.",
                "full_desc": "Network protocols, architecture, and internet technologies. This course covers the OSI model, TCP/IP, routing, and network security. Students will analyze network traffic and implement network applications.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["networking", "protocols", "tcp/ip", "security"],
                "weeks": 14,
                "topics": [
                    "Introduction to Computer Networks",
                    "Network Architecture and OSI Model",
                    "Physical and Data Link Layers",
                    "Ethernet and WiFi",
                    "Network Layer and IP",
                    "Routing Algorithms",
                    "Transport Layer: TCP and UDP",
                    "Congestion Control",
                    "Application Layer Protocols",
                    "DNS and HTTP",
                    "Network Security Basics",
                    "Firewalls and VPNs",
                    "Wireless and Mobile Networks",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Cybersecurity Fundamentals",
                "short_desc": "Security principles, cryptography, and threat mitigation.",
                "full_desc": "Security principles, cryptography, and threat mitigation. This course introduces cybersecurity concepts including encryption, authentication, network security, and secure coding practices. Students will learn to identify and mitigate common vulnerabilities.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["cybersecurity", "cryptography", "security", "encryption"],
                "weeks": 14,
                "topics": [
                    "Introduction to Cybersecurity",
                    "Security Principles and CIA Triad",
                    "Cryptography Basics",
                    "Symmetric Encryption",
                    "Public Key Cryptography",
                    "Hash Functions and Digital Signatures",
                    "Authentication and Access Control",
                    "Network Security",
                    "Web Application Security",
                    "SQL Injection and XSS",
                    "Secure Coding Practices",
                    "Malware and Intrusion Detection",
                    "Security Auditing",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Cloud Computing",
                "short_desc": "Cloud platforms, distributed systems, and scalable architectures.",
                "full_desc": "Cloud platforms, distributed systems, and scalable architectures. This course covers AWS, Azure, containerization with Docker, orchestration with Kubernetes, and microservices architecture. Students will deploy and scale cloud applications.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["cloud computing", "aws", "docker", "kubernetes"],
                "weeks": 14,
                "topics": [
                    "Introduction to Cloud Computing",
                    "Cloud Service Models: IaaS, PaaS, SaaS",
                    "AWS Fundamentals",
                    "Azure and GCP Overview",
                    "Virtual Machines and Compute",
                    "Storage Services",
                    "Containerization with Docker",
                    "Kubernetes Basics",
                    "Microservices Architecture",
                    "Serverless Computing",
                    "Load Balancing and Auto-scaling",
                    "Cloud Security",
                    "Cost Optimization",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Machine Learning Fundamentals",
                "short_desc": "Introduction to machine learning algorithms and applications.",
                "full_desc": "Introduction to machine learning algorithms and applications. This course covers supervised and unsupervised learning, neural networks, and deep learning. Students will learn to implement ML algorithms from scratch and use popular frameworks like scikit-learn and TensorFlow.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["machine learning", "ai", "data science", "python"],
                "weeks": 15,
                "topics": [
                    "Introduction to Machine Learning",
                    "Linear Regression and Gradient Descent",
                    "Logistic Regression and Classification",
                    "Decision Trees and Random Forests",
                    "Support Vector Machines",
                    "K-Nearest Neighbors",
                    "Clustering: K-Means and Hierarchical",
                    "Dimensionality Reduction: PCA",
                    "Neural Network Fundamentals",
                    "Backpropagation and Training",
                    "Model Evaluation and Validation",
                    "Regularization Techniques",
                    "Ensemble Methods",
                    "ML Pipeline and Deployment",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Deep Learning and Neural Networks",
                "short_desc": "Advanced neural network architectures and deep learning techniques.",
                "full_desc": "Advanced neural network architectures and deep learning techniques. This course explores convolutional neural networks, recurrent networks, transformers, and generative models. Students will implement state-of-the-art architectures using PyTorch and apply them to real-world problems in vision, language, and beyond.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["deep learning", "neural networks", "pytorch", "ai"],
                "weeks": 15,
                "topics": [
                    "Deep Learning Foundations",
                    "Convolutional Neural Networks",
                    "CNN Architectures: ResNet, VGG",
                    "Recurrent Neural Networks",
                    "LSTM and GRU Networks",
                    "Sequence-to-Sequence Models",
                    "Attention Mechanisms",
                    "Transformer Architecture",
                    "Generative Adversarial Networks",
                    "Variational Autoencoders",
                    "Transfer Learning",
                    "Model Optimization and Pruning",
                    "Distributed Training",
                    "Ethics in AI",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Natural Language Processing",
                "short_desc": "Text processing, language models, and NLP applications.",
                "full_desc": "Text processing, language models, and NLP applications. This course covers the fundamentals of computational linguistics, from tokenization to large language models. Students will build text classifiers, named entity recognizers, and chatbots using modern NLP techniques and transformer-based models.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["nlp", "language models", "transformers", "text processing"],
                "weeks": 15,
                "topics": [
                    "Introduction to NLP",
                    "Text Preprocessing and Tokenization",
                    "Word Embeddings: Word2Vec, GloVe",
                    "Text Classification",
                    "Named Entity Recognition",
                    "Part-of-Speech Tagging",
                    "Sentiment Analysis",
                    "Language Models: N-grams to Neural",
                    "Sequence-to-Sequence for NLP",
                    "Attention and Transformers for NLP",
                    "BERT and Pre-trained Models",
                    "GPT and Generative Models",
                    "Question Answering Systems",
                    "Chatbots and Dialogue Systems",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Computer Vision",
                "short_desc": "Image processing, object detection, and visual recognition.",
                "full_desc": "Image processing, object detection, and visual recognition. This course teaches how computers interpret visual information, from basic image processing to advanced deep learning for vision. Students will implement object detection, image segmentation, and facial recognition systems.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["computer vision", "image processing", "object detection", "deep learning"],
                "weeks": 15,
                "topics": [
                    "Introduction to Computer Vision",
                    "Image Formation and Representation",
                    "Image Filtering and Enhancement",
                    "Edge Detection and Features",
                    "Feature Descriptors: SIFT, ORB",
                    "Image Classification with CNNs",
                    "Object Detection: YOLO, Faster R-CNN",
                    "Semantic Segmentation",
                    "Instance Segmentation",
                    "Face Detection and Recognition",
                    "Pose Estimation",
                    "Video Analysis and Tracking",
                    "3D Vision and Depth Estimation",
                    "Vision Transformers",
                    "Final Project Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Data Science and Analytics",
                "short_desc": "Data analysis, visualization, and statistical modeling.",
                "full_desc": "Data analysis, visualization, and statistical modeling. This course teaches data wrangling, exploratory data analysis, and statistical inference using Python. Students will work with pandas, matplotlib, and scikit-learn to extract insights from real-world datasets.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["data science", "analytics", "statistics", "visualization"],
                "weeks": 14,
                "topics": [
                    "Introduction to Data Science",
                    "Data Wrangling with Pandas",
                    "Exploratory Data Analysis",
                    "Data Visualization with Matplotlib",
                    "Statistical Inference",
                    "Hypothesis Testing",
                    "Regression Analysis",
                    "Time Series Analysis",
                    "A/B Testing",
                    "Feature Engineering",
                    "Model Selection",
                    "Data Ethics",
                    "Final Project",
                    "Final Presentations",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Mobile App Development",
                "short_desc": "iOS and Android development with React Native.",
                "full_desc": "iOS and Android development with React Native. This course covers mobile UI design, navigation, state management, and API integration. Students will build and deploy cross-platform mobile applications.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["mobile development", "react native", "ios", "android"],
                "weeks": 14,
                "topics": [
                    "Introduction to Mobile Development",
                    "React Native Fundamentals",
                    "Mobile UI Components",
                    "Navigation and Routing",
                    "State Management",
                    "Forms and User Input",
                    "API Integration",
                    "Local Storage",
                    "Camera and Media",
                    "Push Notifications",
                    "App Performance",
                    "Testing Mobile Apps",
                    "App Deployment",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Artificial Intelligence",
                "short_desc": "Search algorithms, knowledge representation, and AI agents.",
                "full_desc": "Search algorithms, knowledge representation, and AI agents. This course covers classical AI techniques including search, logic, planning, and reasoning. Students will implement intelligent agents and explore modern AI applications.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["artificial intelligence", "search", "logic", "agents"],
                "weeks": 15,
                "topics": [
                    "Introduction to AI",
                    "Intelligent Agents",
                    "Search Algorithms: BFS, DFS",
                    "Informed Search: A*",
                    "Adversarial Search and Game Playing",
                    "Constraint Satisfaction Problems",
                    "Logic and Knowledge Representation",
                    "First-Order Logic",
                    "Planning and Acting",
                    "Probabilistic Reasoning",
                    "Bayesian Networks",
                    "Markov Decision Processes",
                    "Reinforcement Learning Basics",
                    "AI Ethics and Safety",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Reinforcement Learning",
                "short_desc": "Agent learning through interaction and reward signals.",
                "full_desc": "Agent learning through interaction and reward signals. This course covers MDPs, Q-learning, policy gradients, and deep reinforcement learning. Students will train agents to play games and solve control problems.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["reinforcement learning", "q-learning", "deep rl", "agents"],
                "weeks": 14,
                "topics": [
                    "Introduction to RL",
                    "Markov Decision Processes",
                    "Dynamic Programming",
                    "Monte Carlo Methods",
                    "Temporal Difference Learning",
                    "Q-Learning",
                    "SARSA and On-Policy Methods",
                    "Function Approximation",
                    "Deep Q-Networks (DQN)",
                    "Policy Gradient Methods",
                    "Actor-Critic Algorithms",
                    "Proximal Policy Optimization",
                    "Multi-Agent RL",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Big Data Technologies",
                "short_desc": "Hadoop, Spark, and distributed data processing.",
                "full_desc": "Hadoop, Spark, and distributed data processing. This course covers big data architectures, MapReduce, Spark, and stream processing. Students will process large-scale datasets using distributed computing frameworks.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["big data", "hadoop", "spark", "distributed systems"],
                "weeks": 14,
                "topics": [
                    "Introduction to Big Data",
                    "Distributed File Systems",
                    "Hadoop Ecosystem",
                    "MapReduce Programming",
                    "Apache Spark Fundamentals",
                    "Spark RDDs and DataFrames",
                    "Spark SQL",
                    "Spark Streaming",
                    "Data Pipelines",
                    "NoSQL Databases",
                    "Data Lakes",
                    "Real-time Analytics",
                    "Performance Tuning",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "CS",
                "department": "Computer Science",
                "title": "Human-Computer Interaction",
                "short_desc": "User interface design, usability, and user experience.",
                "full_desc": "User interface design, usability, and user experience. This course covers design principles, prototyping, user research, and evaluation methods. Students will design and test interactive systems.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["hci", "ui design", "ux", "usability"],
                "weeks": 14,
                "topics": [
                    "Introduction to HCI",
                    "Design Principles",
                    "User-Centered Design",
                    "User Research Methods",
                    "Personas and Scenarios",
                    "Prototyping Techniques",
                    "Wireframing and Mockups",
                    "Interaction Design",
                    "Visual Design",
                    "Usability Testing",
                    "Accessibility",
                    "Mobile and Touch Interfaces",
                    "Design Critique",
                    "Final Project",
                ],
            },

            # ============================================================
            # MATHEMATICS (10 courses)
            # ============================================================
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Linear Algebra for Machine Learning",
                "short_desc": "Vectors, matrices, and linear transformations for ML applications.",
                "full_desc": "Vectors, matrices, and linear transformations for ML applications. This course provides the mathematical foundation essential for understanding machine learning algorithms. Topics include vector spaces, eigenvalues, SVD, and their applications in dimensionality reduction, recommendation systems, and neural networks.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["linear algebra", "mathematics", "machine learning", "vectors"],
                "weeks": 14,
                "topics": [
                    "Vectors and Vector Spaces",
                    "Matrix Operations",
                    "Systems of Linear Equations",
                    "Linear Independence and Basis",
                    "Linear Transformations",
                    "Determinants",
                    "Eigenvalues and Eigenvectors",
                    "Diagonalization",
                    "Singular Value Decomposition",
                    "Principal Component Analysis",
                    "Matrix Factorization",
                    "Norms and Inner Products",
                    "Applications in ML",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Pre-Calculus",
                "short_desc": "Functions, trigonometry, and preparation for calculus.",
                "full_desc": "Functions, trigonometry, and preparation for calculus. This course builds the algebraic and trigonometric foundations needed for success in calculus. Students will master functions, graphs, exponentials, logarithms, and trigonometric identities through problem-solving and applications.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["precalculus", "algebra", "trigonometry", "functions"],
                "weeks": 14,
                "topics": [
                    "Real Numbers and Algebraic Expressions",
                    "Equations and Inequalities",
                    "Functions and Their Graphs",
                    "Polynomial Functions",
                    "Rational Functions",
                    "Exponential Functions",
                    "Logarithmic Functions",
                    "Trigonometric Functions",
                    "Unit Circle and Radians",
                    "Trigonometric Identities",
                    "Inverse Trigonometric Functions",
                    "Sequences and Series",
                    "Conic Sections",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Calculus I",
                "short_desc": "Limits, derivatives, and introduction to integration.",
                "full_desc": "Limits, derivatives, and introduction to integration. This course covers single-variable calculus, including limits, continuity, differentiation, and basic integration. Students will apply calculus to optimization problems, related rates, and area calculations.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["calculus", "derivatives", "integrals", "mathematics"],
                "weeks": 15,
                "topics": [
                    "Limits and Continuity",
                    "Definition of the Derivative",
                    "Differentiation Rules",
                    "Chain Rule",
                    "Implicit Differentiation",
                    "Related Rates",
                    "Linear Approximation",
                    "Maximum and Minimum Values",
                    "Optimization Problems",
                    "Curve Sketching",
                    "Antiderivatives",
                    "Definite Integrals",
                    "Fundamental Theorem of Calculus",
                    "Integration Techniques",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Calculus II",
                "short_desc": "Integration techniques, sequences, series, and parametric equations.",
                "full_desc": "Integration techniques, sequences, series, and parametric equations. This course continues single-variable calculus with advanced integration methods, infinite series, and parametric curves. Applications include arc length, surface area, and Taylor series.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["calculus", "integration", "series", "mathematics"],
                "weeks": 15,
                "topics": [
                    "Integration by Parts",
                    "Trigonometric Integrals",
                    "Partial Fractions",
                    "Improper Integrals",
                    "Applications of Integration",
                    "Sequences",
                    "Infinite Series",
                    "Convergence Tests",
                    "Power Series",
                    "Taylor and Maclaurin Series",
                    "Parametric Equations",
                    "Polar Coordinates",
                    "Arc Length and Surface Area",
                    "Differential Equations Introduction",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Multivariable Calculus",
                "short_desc": "Calculus of functions of several variables.",
                "full_desc": "Calculus of functions of several variables. This course extends calculus to multiple dimensions, covering partial derivatives, multiple integrals, vector calculus, and applications to physics and engineering.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["calculus", "multivariable", "vector calculus", "mathematics"],
                "weeks": 15,
                "topics": [
                    "Functions of Several Variables",
                    "Partial Derivatives",
                    "Chain Rule for Multiple Variables",
                    "Gradient and Directional Derivatives",
                    "Optimization in Multiple Dimensions",
                    "Lagrange Multipliers",
                    "Double Integrals",
                    "Triple Integrals",
                    "Change of Variables",
                    "Vector Fields",
                    "Line Integrals",
                    "Green's Theorem",
                    "Surface Integrals",
                    "Stokes' and Divergence Theorems",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Differential Equations",
                "short_desc": "Ordinary differential equations and applications.",
                "full_desc": "Ordinary differential equations and applications. This course covers first and second-order ODEs, systems of equations, and Laplace transforms. Applications include population dynamics, circuits, and mechanical systems.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["differential equations", "odes", "mathematics", "modeling"],
                "weeks": 14,
                "topics": [
                    "Introduction to Differential Equations",
                    "First-Order ODEs",
                    "Separable Equations",
                    "Linear First-Order Equations",
                    "Exact Equations",
                    "Second-Order Linear ODEs",
                    "Homogeneous Equations",
                    "Non-Homogeneous Equations",
                    "Systems of ODEs",
                    "Matrix Methods",
                    "Laplace Transforms",
                    "Series Solutions",
                    "Applications to Physics",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Probability and Statistics",
                "short_desc": "Probability theory, distributions, and statistical inference.",
                "full_desc": "Probability theory, distributions, and statistical inference. This course covers probability axioms, random variables, common distributions, hypothesis testing, and regression. Students will apply statistical methods to real-world data.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["probability", "statistics", "inference", "data analysis"],
                "weeks": 14,
                "topics": [
                    "Probability Basics",
                    "Conditional Probability",
                    "Random Variables",
                    "Discrete Distributions",
                    "Continuous Distributions",
                    "Normal Distribution",
                    "Central Limit Theorem",
                    "Sampling Distributions",
                    "Point Estimation",
                    "Confidence Intervals",
                    "Hypothesis Testing",
                    "Chi-Square Tests",
                    "Linear Regression",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Discrete Mathematics",
                "short_desc": "Logic, sets, combinatorics, and graph theory.",
                "full_desc": "Logic, sets, combinatorics, and graph theory. This course provides the mathematical foundations for computer science, covering propositional logic, proof techniques, counting, and discrete structures.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["discrete math", "logic", "combinatorics", "graph theory"],
                "weeks": 14,
                "topics": [
                    "Propositional Logic",
                    "Predicate Logic",
                    "Proof Techniques",
                    "Mathematical Induction",
                    "Sets and Set Operations",
                    "Functions and Relations",
                    "Counting Principles",
                    "Permutations and Combinations",
                    "Binomial Theorem",
                    "Graph Theory Basics",
                    "Trees and Spanning Trees",
                    "Euler and Hamiltonian Paths",
                    "Recurrence Relations",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Abstract Algebra",
                "short_desc": "Groups, rings, and fields.",
                "full_desc": "Groups, rings, and fields. This course introduces abstract algebraic structures and their properties. Topics include group theory, ring theory, and applications to cryptography and coding theory.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["abstract algebra", "groups", "rings", "mathematics"],
                "weeks": 15,
                "topics": [
                    "Introduction to Groups",
                    "Subgroups and Cyclic Groups",
                    "Permutation Groups",
                    "Cosets and Lagrange's Theorem",
                    "Normal Subgroups",
                    "Quotient Groups",
                    "Homomorphisms and Isomorphisms",
                    "Introduction to Rings",
                    "Integral Domains",
                    "Fields",
                    "Polynomial Rings",
                    "Ideals and Quotient Rings",
                    "Applications to Cryptography",
                    "Galois Theory Introduction",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "MATH",
                "department": "Mathematics",
                "title": "Numerical Analysis",
                "short_desc": "Numerical methods for solving mathematical problems.",
                "full_desc": "Numerical methods for solving mathematical problems. This course covers algorithms for root finding, interpolation, numerical integration, and solving differential equations. Students will implement methods in Python or MATLAB.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["numerical analysis", "algorithms", "computation", "mathematics"],
                "weeks": 14,
                "topics": [
                    "Error Analysis",
                    "Root Finding: Bisection Method",
                    "Newton's Method",
                    "Fixed-Point Iteration",
                    "Interpolation",
                    "Polynomial Approximation",
                    "Numerical Differentiation",
                    "Numerical Integration",
                    "Gaussian Quadrature",
                    "Solving Linear Systems",
                    "LU Decomposition",
                    "Iterative Methods",
                    "Numerical ODEs",
                    "Final Project",
                ],
            },

            # ============================================================
            # BIOLOGY (10 courses)
            # ============================================================
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Molecular Biology and Genetics",
                "short_desc": "DNA, RNA, protein synthesis, and genetic inheritance.",
                "full_desc": "DNA, RNA, protein synthesis, and genetic inheritance. This course explores the molecular basis of life, from DNA replication to gene expression. Students will learn about genetic mutations, inheritance patterns, and modern techniques like PCR and CRISPR. Laboratory sessions provide hands-on experience with molecular biology techniques.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["biology", "genetics", "dna", "molecular biology"],
                "weeks": 15,
                "topics": [
                    "Introduction to Molecular Biology",
                    "DNA Structure and Replication",
                    "RNA and Transcription",
                    "Protein Synthesis and Translation",
                    "Gene Regulation in Prokaryotes",
                    "Gene Regulation in Eukaryotes",
                    "Mendelian Genetics",
                    "Chromosomal Inheritance",
                    "DNA Mutations and Repair",
                    "Recombinant DNA Technology",
                    "PCR and Gel Electrophoresis",
                    "CRISPR and Gene Editing",
                    "Genomics and Bioinformatics",
                    "Genetic Diseases",
                    "Final Lab Practical",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Marine Ecology and Conservation",
                "short_desc": "Ocean ecosystems, biodiversity, and conservation strategies.",
                "full_desc": "Ocean ecosystems, biodiversity, and conservation strategies. This course examines marine habitats from coral reefs to deep sea vents, exploring species interactions, food webs, and human impacts. Students will analyze case studies of marine conservation efforts and develop proposals for protecting endangered marine ecosystems.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["marine biology", "ecology", "conservation", "oceanography"],
                "weeks": 14,
                "topics": [
                    "Introduction to Marine Ecosystems",
                    "Physical Oceanography",
                    "Marine Primary Production",
                    "Coral Reef Ecosystems",
                    "Coastal and Estuarine Habitats",
                    "Deep Sea Environments",
                    "Marine Food Webs",
                    "Fish Biology and Fisheries",
                    "Marine Mammals and Reptiles",
                    "Climate Change and Ocean Acidification",
                    "Pollution and Plastic in Oceans",
                    "Marine Protected Areas",
                    "Conservation Case Studies",
                    "Final Conservation Proposals",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Introduction to Biology",
                "short_desc": "Fundamental concepts of life, cells, and evolution.",
                "full_desc": "Fundamental concepts of life, cells, and evolution. This introductory course covers cell structure, metabolism, genetics, evolution, and ecology. Designed for non-majors and beginning biology students.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["biology", "cells", "evolution", "introductory"],
                "weeks": 14,
                "topics": [
                    "Introduction to Life Science",
                    "Chemistry of Life",
                    "Cell Structure and Function",
                    "Cell Membrane and Transport",
                    "Cellular Respiration",
                    "Photosynthesis",
                    "Cell Division: Mitosis and Meiosis",
                    "Mendelian Genetics",
                    "DNA and Molecular Genetics",
                    "Evolution and Natural Selection",
                    "Biodiversity",
                    "Ecology and Ecosystems",
                    "Human Impact on Environment",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Human Anatomy and Physiology",
                "short_desc": "Structure and function of human body systems.",
                "full_desc": "Structure and function of human body systems. This course examines the organization of the human body from cells to organ systems. Topics include skeletal, muscular, nervous, cardiovascular, and other major systems.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["anatomy", "physiology", "human biology", "health"],
                "weeks": 15,
                "topics": [
                    "Introduction to Anatomy and Physiology",
                    "Cells and Tissues",
                    "Integumentary System",
                    "Skeletal System",
                    "Muscular System",
                    "Nervous System",
                    "Sensory Systems",
                    "Endocrine System",
                    "Cardiovascular System",
                    "Respiratory System",
                    "Digestive System",
                    "Urinary System",
                    "Reproductive System",
                    "Immune System",
                    "Final Lab Practical",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Microbiology",
                "short_desc": "Bacteria, viruses, fungi, and their roles in health and disease.",
                "full_desc": "Bacteria, viruses, fungi, and their roles in health and disease. This course covers microbial structure, metabolism, genetics, and interactions with humans. Laboratory work includes culturing and identifying microorganisms.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["microbiology", "bacteria", "viruses", "pathogens"],
                "weeks": 15,
                "topics": [
                    "Introduction to Microbiology",
                    "Bacterial Cell Structure",
                    "Microbial Metabolism",
                    "Microbial Growth",
                    "Control of Microorganisms",
                    "Microbial Genetics",
                    "Viruses and Prions",
                    "Fungi and Parasites",
                    "Immunology Basics",
                    "Infectious Diseases",
                    "Epidemiology",
                    "Antibiotics and Resistance",
                    "Environmental Microbiology",
                    "Industrial Microbiology",
                    "Final Lab Practical",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Ecology and Environmental Science",
                "short_desc": "Ecosystems, populations, and environmental challenges.",
                "full_desc": "Ecosystems, populations, and environmental challenges. This course examines interactions between organisms and their environment, population dynamics, community ecology, and conservation biology.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["ecology", "environment", "conservation", "sustainability"],
                "weeks": 14,
                "topics": [
                    "Introduction to Ecology",
                    "Population Ecology",
                    "Population Growth Models",
                    "Community Ecology",
                    "Species Interactions",
                    "Ecosystem Ecology",
                    "Energy Flow and Nutrient Cycling",
                    "Biodiversity",
                    "Biogeography",
                    "Climate Change Biology",
                    "Conservation Biology",
                    "Habitat Loss and Fragmentation",
                    "Restoration Ecology",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Biochemistry",
                "short_desc": "Chemical processes and molecules of living organisms.",
                "full_desc": "Chemical processes and molecules of living organisms. This course covers the structure and function of biological macromolecules, enzyme kinetics, metabolism, and molecular signaling.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["biochemistry", "metabolism", "enzymes", "proteins"],
                "weeks": 15,
                "topics": [
                    "Introduction to Biochemistry",
                    "Amino Acids and Proteins",
                    "Protein Structure",
                    "Enzyme Kinetics",
                    "Enzyme Regulation",
                    "Carbohydrates",
                    "Lipids and Membranes",
                    "Nucleic Acids",
                    "Glycolysis",
                    "Citric Acid Cycle",
                    "Oxidative Phosphorylation",
                    "Photosynthesis Biochemistry",
                    "Lipid Metabolism",
                    "Amino Acid Metabolism",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Neuroscience",
                "short_desc": "Brain structure, neural circuits, and behavior.",
                "full_desc": "Brain structure, neural circuits, and behavior. This course explores the nervous system from molecules to behavior, covering neuroanatomy, synaptic transmission, sensory systems, and cognitive neuroscience.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["neuroscience", "brain", "neurons", "cognition"],
                "weeks": 15,
                "topics": [
                    "Introduction to Neuroscience",
                    "Neuroanatomy",
                    "Neurons and Glia",
                    "Membrane Potential",
                    "Action Potentials",
                    "Synaptic Transmission",
                    "Neurotransmitters",
                    "Sensory Systems",
                    "Motor Systems",
                    "Learning and Memory",
                    "Emotion and Motivation",
                    "Language and Cognition",
                    "Neurological Disorders",
                    "Psychiatric Disorders",
                    "Final Exam Review",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Evolutionary Biology",
                "short_desc": "Mechanisms of evolution and phylogenetics.",
                "full_desc": "Mechanisms of evolution and phylogenetics. This course examines natural selection, genetic drift, speciation, and the history of life on Earth. Students will analyze evolutionary patterns using molecular and morphological data.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["evolution", "phylogenetics", "natural selection", "speciation"],
                "weeks": 14,
                "topics": [
                    "Introduction to Evolution",
                    "Evidence for Evolution",
                    "Natural Selection",
                    "Genetic Variation",
                    "Hardy-Weinberg Equilibrium",
                    "Genetic Drift",
                    "Gene Flow and Migration",
                    "Mutation",
                    "Sexual Selection",
                    "Speciation",
                    "Phylogenetics",
                    "Molecular Evolution",
                    "Coevolution",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Cell Biology",
                "short_desc": "Advanced study of cell structure and function.",
                "full_desc": "Advanced study of cell structure and function. This course provides an in-depth examination of cellular organelles, cell signaling, cell cycle, and cellular techniques. Laboratory work includes microscopy and cell culture.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["cell biology", "organelles", "cell signaling", "microscopy"],
                "weeks": 15,
                "topics": [
                    "Cell Theory and Methods",
                    "Membrane Structure and Function",
                    "Membrane Transport",
                    "Organelles and Compartments",
                    "Protein Trafficking",
                    "Cytoskeleton",
                    "Cell Signaling Pathways",
                    "Cell Cycle",
                    "Mitosis and Cytokinesis",
                    "Apoptosis",
                    "Cancer Biology",
                    "Stem Cells",
                    "Cell Culture Techniques",
                    "Microscopy Techniques",
                    "Final Lab Practical",
                ],
            },
            {
                "code_prefix": "BIO",
                "department": "Biology",
                "title": "Bioinformatics",
                "short_desc": "Computational analysis of biological data.",
                "full_desc": "Computational analysis of biological data. This course teaches algorithms and tools for analyzing genomic, proteomic, and other biological datasets. Students will learn sequence alignment, phylogenetic analysis, and structural bioinformatics.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["bioinformatics", "genomics", "computational biology", "data analysis"],
                "weeks": 14,
                "topics": [
                    "Introduction to Bioinformatics",
                    "Biological Databases",
                    "Sequence Alignment",
                    "BLAST and Homology Search",
                    "Multiple Sequence Alignment",
                    "Phylogenetic Trees",
                    "Genome Assembly",
                    "Gene Prediction",
                    "RNA-Seq Analysis",
                    "Protein Structure Prediction",
                    "Molecular Docking",
                    "Systems Biology",
                    "Machine Learning in Biology",
                    "Final Project",
                ],
            },

            # ============================================================
            # ARCHITECTURE (10 courses)
            # ============================================================
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Introduction to Architecture",
                "short_desc": "Fundamentals of architectural design and history.",
                "full_desc": "Fundamentals of architectural design and history. This course introduces students to architectural principles, design thinking, and the history of built environments. Students will develop basic drawing and modeling skills.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["architecture", "design", "history", "fundamentals"],
                "weeks": 14,
                "topics": [
                    "Introduction to Architecture",
                    "Elements of Design",
                    "Architectural Drawing Basics",
                    "Scale and Proportion",
                    "Ancient Architecture",
                    "Medieval Architecture",
                    "Renaissance Architecture",
                    "Modern Architecture",
                    "Contemporary Architecture",
                    "Site Analysis",
                    "Form and Space",
                    "Materials and Construction",
                    "Design Studio Project",
                    "Final Presentations",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Architectural Drawing and Representation",
                "short_desc": "Technical drawing, CAD, and visualization techniques.",
                "full_desc": "Technical drawing, CAD, and visualization techniques. This course teaches orthographic projection, perspective drawing, and computer-aided design using AutoCAD and Revit. Students will create professional architectural drawings.",
                "difficulty": DifficultyLevel.BEGINNER,
                "credits": 3,
                "tags": ["architecture", "cad", "drawing", "visualization"],
                "weeks": 14,
                "topics": [
                    "Drafting Fundamentals",
                    "Orthographic Projection",
                    "Plans, Sections, Elevations",
                    "Perspective Drawing",
                    "Axonometric Drawing",
                    "Introduction to AutoCAD",
                    "2D CAD Techniques",
                    "Introduction to Revit",
                    "BIM Fundamentals",
                    "3D Modeling",
                    "Rendering Techniques",
                    "Presentation Graphics",
                    "Portfolio Development",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Architectural Design Studio I",
                "short_desc": "Residential design and small-scale projects.",
                "full_desc": "Residential design and small-scale projects. This studio course focuses on designing single-family homes and small buildings. Students will develop design concepts, create drawings, and build physical models.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 4,
                "tags": ["architecture", "design studio", "residential", "design"],
                "weeks": 15,
                "topics": [
                    "Design Process",
                    "Site Analysis and Context",
                    "Program Development",
                    "Conceptual Design",
                    "Schematic Design",
                    "Space Planning",
                    "Circulation and Flow",
                    "Design Development",
                    "Material Selection",
                    "Structural Considerations",
                    "Building Systems Integration",
                    "Model Making",
                    "Design Critique",
                    "Final Review",
                    "Portfolio Documentation",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Structures and Building Systems",
                "short_desc": "Structural principles and mechanical systems.",
                "full_desc": "Structural principles and mechanical systems. This course covers structural analysis, load paths, and building systems including HVAC, plumbing, and electrical. Students will design structural systems for buildings.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["architecture", "structures", "building systems", "engineering"],
                "weeks": 14,
                "topics": [
                    "Structural Principles",
                    "Forces and Loads",
                    "Structural Materials",
                    "Beams and Columns",
                    "Trusses and Frames",
                    "Foundations",
                    "Lateral Load Systems",
                    "HVAC Systems",
                    "Plumbing Systems",
                    "Electrical Systems",
                    "Fire Protection",
                    "Acoustics",
                    "Lighting Design",
                    "Final Exam",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Urban Design and Planning",
                "short_desc": "City planning, public spaces, and urban development.",
                "full_desc": "City planning, public spaces, and urban development. This course examines urban form, zoning, transportation, and community design. Students will develop plans for urban neighborhoods and public spaces.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["urban design", "planning", "public space", "cities"],
                "weeks": 14,
                "topics": [
                    "History of Urban Planning",
                    "Urban Form and Morphology",
                    "Zoning and Land Use",
                    "Transportation Planning",
                    "Public Transit Systems",
                    "Pedestrian and Bicycle Planning",
                    "Public Space Design",
                    "Parks and Recreation",
                    "Mixed-Use Development",
                    "Smart Growth",
                    "Community Engagement",
                    "Urban Sustainability",
                    "Case Studies",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Sustainable Building Design",
                "short_desc": "Green architecture, energy efficiency, and LEED certification.",
                "full_desc": "Green architecture, energy efficiency, and LEED certification. This course teaches sustainable design principles for buildings that minimize environmental impact. Students will learn about passive solar design, green materials, water conservation, and renewable energy integration. Projects focus on designing net-zero energy buildings.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 4,
                "tags": ["architecture", "sustainability", "green building", "leed"],
                "weeks": 15,
                "topics": [
                    "Principles of Sustainable Design",
                    "Climate-Responsive Architecture",
                    "Passive Solar Design",
                    "Building Envelope and Insulation",
                    "Natural Ventilation Strategies",
                    "Daylighting and Lighting Design",
                    "Sustainable Materials Selection",
                    "Water Conservation Systems",
                    "Renewable Energy Integration",
                    "LEED Certification Process",
                    "Life Cycle Assessment",
                    "Green Roofs and Living Walls",
                    "Net-Zero Building Design",
                    "Case Studies of Green Buildings",
                    "Final Design Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Historic Preservation",
                "short_desc": "Conservation of historic buildings and cultural heritage.",
                "full_desc": "Conservation of historic buildings and cultural heritage. This course covers documentation, assessment, and restoration of historic structures. Students will learn preservation standards and develop conservation plans.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["architecture", "preservation", "historic", "conservation"],
                "weeks": 14,
                "topics": [
                    "Introduction to Preservation",
                    "History of Preservation Movement",
                    "Documentation Techniques",
                    "Historic Building Assessment",
                    "Materials Conservation",
                    "Structural Stabilization",
                    "Restoration vs. Rehabilitation",
                    "Adaptive Reuse",
                    "Preservation Standards",
                    "Cultural Heritage",
                    "Heritage Tourism",
                    "Legal and Regulatory Framework",
                    "Case Studies",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Landscape Architecture",
                "short_desc": "Design of outdoor spaces, parks, and landscapes.",
                "full_desc": "Design of outdoor spaces, parks, and landscapes. This course covers site planning, planting design, grading, and landscape construction. Students will design parks, gardens, and public landscapes.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["landscape architecture", "site design", "parks", "outdoor spaces"],
                "weeks": 14,
                "topics": [
                    "Introduction to Landscape Architecture",
                    "Site Analysis",
                    "Topography and Grading",
                    "Drainage and Hydrology",
                    "Planting Design",
                    "Plant Selection",
                    "Hardscape Materials",
                    "Paving and Pathways",
                    "Site Furniture",
                    "Irrigation Systems",
                    "Sustainable Landscapes",
                    "Rain Gardens and Bioswales",
                    "Park Design",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Interior Architecture",
                "short_desc": "Interior space planning and design.",
                "full_desc": "Interior space planning and design. This course focuses on the design of interior environments including residential, commercial, and institutional spaces. Topics include space planning, materials, lighting, and furniture.",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "credits": 3,
                "tags": ["interior design", "space planning", "materials", "lighting"],
                "weeks": 14,
                "topics": [
                    "Introduction to Interior Architecture",
                    "Space Planning Principles",
                    "Residential Interiors",
                    "Commercial Interiors",
                    "Hospitality Design",
                    "Retail Design",
                    "Office Design",
                    "Interior Materials",
                    "Finishes and Surfaces",
                    "Furniture Design",
                    "Interior Lighting",
                    "Color Theory",
                    "Accessibility and Universal Design",
                    "Final Project",
                ],
            },
            {
                "code_prefix": "ARCH",
                "department": "Architecture",
                "title": "Digital Fabrication",
                "short_desc": "3D printing, CNC, and computational design.",
                "full_desc": "3D printing, CNC, and computational design. This course explores digital fabrication technologies and parametric design. Students will use Grasshopper, laser cutters, and 3D printers to create architectural prototypes.",
                "difficulty": DifficultyLevel.ADVANCED,
                "credits": 3,
                "tags": ["digital fabrication", "3d printing", "parametric design", "technology"],
                "weeks": 14,
                "topics": [
                    "Introduction to Digital Fabrication",
                    "Parametric Design Basics",
                    "Grasshopper for Rhino",
                    "Algorithmic Design",
                    "3D Modeling for Fabrication",
                    "3D Printing Technologies",
                    "Laser Cutting",
                    "CNC Milling",
                    "Robotic Fabrication",
                    "Material Exploration",
                    "Prototyping Techniques",
                    "Digital Craft",
                    "Design-to-Fabrication Workflow",
                    "Final Project",
                ],
            },
        ]

    def _generate_course_from_template(
        self, template: Dict[str, Any], course_num: int
    ) -> HierarchicalCourse:
        """Generate a complete hierarchical course from template."""

        course_code = f"{template['code_prefix']}{course_num:03d}"
        instructor = fake.name()

        # Generate syllabus
        syllabus = self._generate_syllabus(template)

        # Generate assignments
        assignments = self._generate_assignments(template["weeks"])

        # Generate prerequisites
        prerequisites = self._generate_prerequisites(template, course_num)

        # Create summary
        summary = CourseSummary(
            course_code=course_code,
            title=template["title"],
            department=template["department"],
            credits=template["credits"],
            difficulty_level=template["difficulty"],
            format=random.choice(list(CourseFormat)),
            instructor=instructor,
            short_description=template["short_desc"],
            prerequisite_codes=[p.course_code for p in prerequisites],
            tags=template["tags"],
        )
        summary.generate_embedding_text()

        # Create details
        details = CourseDetails(
            course_code=course_code,
            title=template["title"],
            department=template["department"],
            credits=template["credits"],
            difficulty_level=template["difficulty"],
            format=summary.format,
            instructor=instructor,
            full_description=template["full_desc"],
            prerequisites=prerequisites,
            learning_objectives=self._generate_learning_objectives(template),
            syllabus=syllabus,
            assignments=assignments,
            semester=random.choice(list(Semester)),
            year=2025,
            max_enrollment=random.randint(30, 80),
            tags=template["tags"],
        )

        # Create hierarchical course
        return HierarchicalCourse(
            id=str(ULID()),
            summary=summary,
            details=details,
        )

    def _generate_syllabus(self, template: Dict[str, Any]) -> CourseSyllabus:
        """Generate week-by-week syllabus."""
        weeks = []
        topics = template.get("topics", [])

        for week_num in range(1, template["weeks"] + 1):
            topic = (
                topics[week_num - 1]
                if week_num - 1 < len(topics)
                else f"Week {week_num} Topic"
            )

            week = WeekPlan(
                week_number=week_num,
                topic=topic,
                subtopics=[
                    f"{topic} - Part {i + 1}" for i in range(random.randint(2, 4))
                ],
                readings=[f"Chapter {week_num}", f"Research Paper {week_num}"],
                assignments=self._get_week_assignments(week_num, template["weeks"]),
                learning_objectives=[
                    f"Understand {topic.lower()}",
                    f"Apply {topic.lower()} concepts",
                    f"Implement {topic.lower()} solutions",
                ],
            )
            weeks.append(week)

        return CourseSyllabus(weeks=weeks, total_weeks=template["weeks"])

    def _get_week_assignments(self, week_num: int, total_weeks: int) -> List[str]:
        """Get assignments due in a specific week."""
        assignments = []

        # Homework every 2 weeks
        if week_num % 2 == 0 and week_num < total_weeks - 2:
            assignments.append(f"Homework {week_num // 2}")

        # Midterm
        if week_num == total_weeks // 2:
            assignments.append("Midterm Exam")

        # Final project milestones
        if week_num == total_weeks - 4:
            assignments.append("Project Proposal")
        elif week_num == total_weeks - 2:
            assignments.append("Project Draft")
        elif week_num == total_weeks:
            assignments.append("Final Project")

        return assignments

    def _generate_assignments(self, weeks: int) -> List[Assignment]:
        """Generate course assignments."""
        assignments = []

        # Homeworks (every 2 weeks)
        for i in range(1, weeks // 2):
            assignments.append(
                Assignment(
                    title=f"Homework {i}",
                    description=f"Problem set covering weeks {i * 2 - 1}-{i * 2}",
                    type=AssignmentType.HOMEWORK,
                    due_week=i * 2,
                    points=100,
                    estimated_hours=8.0,
                    submission_format="PDF or Jupyter Notebook",
                )
            )

        # Midterm
        assignments.append(
            Assignment(
                title="Midterm Exam",
                description="Comprehensive exam covering first half of course",
                type=AssignmentType.EXAM,
                due_week=weeks // 2,
                points=200,
                estimated_hours=3.0,
            )
        )

        # Final project
        assignments.extend(
            [
                Assignment(
                    title="Project Proposal",
                    description="1-page proposal for final project",
                    type=AssignmentType.PROJECT,
                    due_week=weeks - 4,
                    points=50,
                    estimated_hours=4.0,
                    group_work=True,
                    submission_format="PDF",
                ),
                Assignment(
                    title="Project Draft",
                    description="Working implementation and preliminary results",
                    type=AssignmentType.PROJECT,
                    due_week=weeks - 2,
                    points=100,
                    estimated_hours=15.0,
                    group_work=True,
                    submission_format="GitHub Repository",
                ),
                Assignment(
                    title="Final Project",
                    description="Complete project with code, report, and presentation",
                    type=AssignmentType.PROJECT,
                    due_week=weeks,
                    points=300,
                    estimated_hours=25.0,
                    group_work=True,
                    submission_format="GitHub + Presentation",
                ),
            ]
        )

        return assignments

    def _generate_prerequisites(
        self, template: Dict[str, Any], course_num: int
    ) -> List[Prerequisite]:
        """Generate prerequisites based on course progression.

        Prerequisites are assigned based on logical course progression:
        - Beginner courses: no prerequisites
        - Intermediate courses: may have beginner prerequisites from same department
        - Advanced courses: have intermediate/beginner prerequisites from same department
        """
        prerequisites = []

        # Define prerequisite mappings based on actual course progression
        prereq_map = {
            # CS prerequisites
            "Data Structures and Algorithms": ["CS001"],  # Intro to Programming
            "Operating Systems": ["CS002"],  # Data Structures
            "Cloud Computing": ["CS007"],  # Computer Networks
            "Machine Learning Fundamentals": ["CS002", "MATH020"],  # Data Structures, Linear Algebra
            "Deep Learning and Neural Networks": ["CS010"],  # ML Fundamentals
            "Natural Language Processing": ["CS010"],  # ML Fundamentals
            "Computer Vision": ["CS010"],  # ML Fundamentals
            "Artificial Intelligence": ["CS002"],  # Data Structures
            "Reinforcement Learning": ["CS010"],  # ML Fundamentals
            "Big Data Technologies": ["CS003"],  # Database Systems

            # Math prerequisites
            "Calculus I": ["MATH021"],  # Pre-Calculus
            "Calculus II": ["MATH022"],  # Calculus I
            "Multivariable Calculus": ["MATH023"],  # Calculus II
            "Differential Equations": ["MATH022"],  # Calculus I
            "Abstract Algebra": ["MATH027"],  # Discrete Mathematics
            "Numerical Analysis": ["MATH022"],  # Calculus I

            # Biology prerequisites
            "Molecular Biology and Genetics": ["BIO032"],  # Intro to Biology
            "Human Anatomy and Physiology": ["BIO032"],  # Intro to Biology
            "Microbiology": ["BIO032"],  # Intro to Biology
            "Ecology and Environmental Science": ["BIO032"],  # Intro to Biology
            "Biochemistry": ["BIO030"],  # Molecular Biology
            "Neuroscience": ["BIO033"],  # Anatomy and Physiology
            "Evolutionary Biology": ["BIO030"],  # Molecular Biology
            "Cell Biology": ["BIO030"],  # Molecular Biology
            "Bioinformatics": ["BIO030", "CS001"],  # Molecular Biology, Programming

            # Architecture prerequisites
            "Architectural Design Studio I": ["ARCH041"],  # Intro to Architecture
            "Structures and Building Systems": ["ARCH041"],  # Intro to Architecture
            "Urban Design and Planning": ["ARCH041"],  # Intro to Architecture
            "Sustainable Building Design": ["ARCH043"],  # Design Studio I
            "Historic Preservation": ["ARCH041"],  # Intro to Architecture
            "Landscape Architecture": ["ARCH041"],  # Intro to Architecture
            "Interior Architecture": ["ARCH041"],  # Intro to Architecture
            "Digital Fabrication": ["ARCH042"],  # Architectural Drawing
        }

        # Check if this course has defined prerequisites
        if template["title"] in prereq_map:
            for prereq_code in prereq_map[template["title"]]:
                prerequisites.append(
                    Prerequisite(
                        course_code=prereq_code,
                        course_title=f"Prerequisite for {template['title']}",
                        minimum_grade="C",
                        can_be_concurrent=False,
                    )
                )

        return prerequisites

    def _generate_learning_objectives(self, template: Dict[str, Any]) -> List[str]:
        """Generate learning objectives."""
        return [
            f"Understand core concepts in {template['title'].lower()}",
            f"Implement {template['title'].lower()} algorithms and techniques",
            f"Apply {template['title'].lower()} to real-world problems",
            f"Analyze and evaluate {template['title'].lower()} solutions",
            f"Design and build complete {template['department'].lower()} systems",
        ]

    def save_to_json(self, output_dir: Path):
        """Save courses to JSON file."""
        output_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "courses": [
                {
                    "id": course.id,
                    "summary": course.summary.model_dump(mode="json"),
                    "details": course.details.model_dump(mode="json"),
                    "created_at": course.created_at.isoformat(),
                }
                for course in self.generated_courses
            ]
        }

        json_file = output_dir / "hierarchical_courses.json"
        with open(json_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"✅ Saved {len(self.generated_courses)} courses to {json_file}")

    def save_to_markdown(self, output_dir: Path):
        """Save courses to human-readable markdown files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create index file
        index_file = output_dir / "COURSE_CATALOG.md"
        with open(index_file, "w") as f:
            f.write("# Course Catalog\n\n")
            f.write(
                f"Generated {len(self.generated_courses)} courses with full syllabi and assignments.\n\n"
            )
            f.write("## Courses by Department\n\n")

            # Group by department
            by_dept = {}
            for course in self.generated_courses:
                dept = course.summary.department
                if dept not in by_dept:
                    by_dept[dept] = []
                by_dept[dept].append(course)

            for dept, courses in sorted(by_dept.items()):
                f.write(f"\n### {dept}\n\n")
                for course in sorted(courses, key=lambda c: c.summary.course_code):
                    f.write(
                        f"- **{course.summary.course_code}**: {course.summary.title}\n"
                    )
                    f.write(f"  - {course.summary.short_description}\n")
                    f.write(
                        f"  - Credits: {course.summary.credits} | Level: {course.summary.difficulty_level.value}\n"
                    )
                    f.write(f"  - [View Details]({course.summary.course_code}.md)\n\n")

        print(f"✅ Created course catalog index: {index_file}")

        # Create individual course files
        for course in self.generated_courses:
            self._save_course_markdown(course, output_dir)

        print(
            f"✅ Created {len(self.generated_courses)} individual course markdown files"
        )

    def _save_course_markdown(self, course: HierarchicalCourse, output_dir: Path):
        """Save individual course to markdown."""
        filename = output_dir / f"{course.summary.course_code}.md"

        with open(filename, "w") as f:
            # Header
            f.write(f"# {course.details.course_code}: {course.details.title}\n\n")

            # Basic info
            f.write("## Course Information\n\n")
            f.write(f"- **Department**: {course.details.department}\n")
            f.write(f"- **Credits**: {course.details.credits}\n")
            f.write(
                f"- **Difficulty Level**: {course.details.difficulty_level.value}\n"
            )
            f.write(f"- **Format**: {course.details.format.value}\n")
            f.write(f"- **Instructor**: {course.details.instructor}\n")
            f.write(
                f"- **Semester**: {course.details.semester.value} {course.details.year}\n"
            )
            f.write(f"- **Max Enrollment**: {course.details.max_enrollment}\n")

            # Description
            f.write(f"\n## Description\n\n{course.details.full_description}\n")

            # Prerequisites
            if course.details.prerequisites:
                f.write(f"\n## Prerequisites\n\n")
                for prereq in course.details.prerequisites:
                    f.write(f"- **{prereq.course_code}**: {prereq.course_title}")
                    if prereq.minimum_grade:
                        f.write(f" (Minimum grade: {prereq.minimum_grade})")
                    f.write("\n")

            # Learning objectives
            f.write(f"\n## Learning Objectives\n\n")
            for obj in course.details.learning_objectives:
                f.write(f"- {obj}\n")

            # Assignments
            f.write(f"\n## Assignments\n\n")
            f.write(f"**Total Points**: {course.details.get_total_points()}\n\n")

            by_type = {}
            for assignment in course.details.assignments:
                if assignment.type not in by_type:
                    by_type[assignment.type] = []
                by_type[assignment.type].append(assignment)

            for assign_type, assignments in sorted(
                by_type.items(), key=lambda x: x[0].value
            ):
                f.write(f"\n### {assign_type.value.title()}s\n\n")
                for assignment in sorted(assignments, key=lambda a: a.due_week):
                    f.write(f"#### {assignment.title} (Week {assignment.due_week})\n\n")
                    f.write(f"{assignment.description}\n\n")
                    f.write(f"- **Points**: {assignment.points}\n")
                    if assignment.estimated_hours:
                        f.write(
                            f"- **Estimated Hours**: {assignment.estimated_hours}\n"
                        )
                    if assignment.group_work:
                        f.write(f"- **Group Work**: Yes\n")
                    if assignment.submission_format:
                        f.write(
                            f"- **Submission Format**: {assignment.submission_format}\n"
                        )
                    f.write("\n")

            # Syllabus
            f.write(
                f"\n## Course Syllabus ({course.details.syllabus.total_weeks} weeks)\n\n"
            )
            for week in course.details.syllabus.weeks:
                f.write(f"\n### Week {week.week_number}: {week.topic}\n\n")

                if week.subtopics:
                    f.write("**Subtopics**:\n")
                    for subtopic in week.subtopics:
                        f.write(f"- {subtopic}\n")
                    f.write("\n")

                if week.learning_objectives:
                    f.write("**Learning Objectives**:\n")
                    for obj in week.learning_objectives:
                        f.write(f"- {obj}\n")
                    f.write("\n")

                if week.readings:
                    f.write("**Readings**:\n")
                    for reading in week.readings:
                        f.write(f"- {reading}\n")
                    f.write("\n")

                if week.assignments:
                    f.write("**Assignments Due**:\n")
                    for assignment in week.assignments:
                        f.write(f"- {assignment}\n")
                    f.write("\n")

            # Tags
            if course.details.tags:
                f.write(f"\n## Tags\n\n")
                f.write(", ".join([f"`{tag}`" for tag in course.details.tags]))
                f.write("\n")


@click.command()
@click.option(
    "--output-dir", "-o", default="generated_courses", help="Output directory"
)
@click.option("--count", "-c", default=50, help="Number of courses to generate")
@click.option("--seed", "-s", type=int, help="Random seed for reproducible generation")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown", "both"]),
    default="both",
    help="Output format",
)
def main(output_dir: str, count: int, seed: int, format: str):
    """Generate hierarchical course catalog with syllabi and assignments."""

    print(f"🎓 Generating {count} courses with full details...\n")

    generator = HierarchicalCourseGenerator(seed=seed)
    courses = generator.generate_courses(count)

    output_path = Path(output_dir)

    if format in ["json", "both"]:
        print("\n📄 Saving to JSON...")
        generator.save_to_json(output_path)

    if format in ["markdown", "both"]:
        print("\n📝 Saving to Markdown...")
        generator.save_to_markdown(output_path)

    print(f"\n✅ Generation complete!")
    print(f"   Total courses: {len(courses)}")
    print(f"   Output directory: {output_path.absolute()}")

    # Print summary statistics
    total_assignments = sum(c.details.get_total_assignments() for c in courses)
    total_weeks = sum(c.details.syllabus.total_weeks for c in courses)

    print(f"\n📊 Statistics:")
    print(f"   Total assignments: {total_assignments}")
    print(f"   Total weeks of content: {total_weeks}")
    print(f"   Average assignments per course: {total_assignments / len(courses):.1f}")
    print(f"   Average weeks per course: {total_weeks / len(courses):.1f}")


if __name__ == "__main__":
    main()
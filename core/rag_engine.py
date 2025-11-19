"""
RAG (Retrieval Augmented Generation) Engine
Retrieves relevant biblical worldview content to guide AI responses
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class BiblicalWorldviewRAG:
    """
    Retrieval engine that prioritizes:
    1. Biblical worldview content
    2. Curriculum-specific knowledge
    3. Scripture references
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.worldview_db = None
        self.curriculum_db = None
        self.scripture_db = None
        self._initialize_knowledge_bases()
    
    def _initialize_knowledge_bases(self):
        """Load and vectorize all knowledge bases"""
        
        print("Loading biblical worldview knowledge base...")
        
        # Priority 1: Biblical Worldview
        worldview_docs = self._load_directory("knowledge_base/biblical_worldview/")
        if worldview_docs:
            self.worldview_db = Chroma.from_documents(
                worldview_docs,
                self.embeddings,
                collection_name="biblical_worldview",
                persist_directory="./chroma_db/worldview"
            )
            print(f"✓ Loaded {len(worldview_docs)} worldview documents")
        
        # Priority 2: Curricula (Saxon, Apologia, Classical)
        curriculum_docs = self._load_directory("knowledge_base/curricula/")
        if curriculum_docs:
            self.curriculum_db = Chroma.from_documents(
                curriculum_docs,
                self.embeddings,
                collection_name="curricula",
                persist_directory="./chroma_db/curricula"
            )
            print(f"✓ Loaded {len(curriculum_docs)} curriculum documents")
        
        # Priority 3: Scripture topical index
        scripture_docs = self._load_directory("knowledge_base/scripture/")
        if scripture_docs:
            self.scripture_db = Chroma.from_documents(
                scripture_docs,
                self.embeddings,
                collection_name="scripture",
                persist_directory="./chroma_db/scripture"
            )
            print(f"✓ Loaded {len(scripture_docs)} scripture documents")
        
        print("Knowledge bases ready!\n")
    
    def _load_directory(self, path):
        """Load all .txt files from directory into Document objects"""
        documents = []
        
        if not os.path.exists(path):
            print(f"Warning: Directory not found: {path}")
            return documents
        
        for filename in os.listdir(path):
            if filename.endswith('.txt'):
                filepath = os.path.join(path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        content = file.read()
                        
                        # Split into chunks for better retrieval
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1000,
                            chunk_overlap=200
                        )
                        chunks = splitter.split_text(content)
                        
                        for chunk in chunks:
                            documents.append(
                                Document(
                                    page_content=chunk,
                                    metadata={"source": filename}
                                )
                            )
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        return documents
    
    def retrieve_context(self, query, subject="general"):
        """
        Retrieve relevant context with biblical worldview prioritized
        Returns: dict with worldview, curriculum, and scripture contexts
        """
        
        context = {
            "worldview": [],
            "curriculum": [],
            "scripture": []
        }
        
        # Always check worldview first for foundational issues
        if self.worldview_db:
            try:
                worldview_results = self.worldview_db.similarity_search(query, k=2)
                context["worldview"] = [doc.page_content for doc in worldview_results]
            except Exception as e:
                print(f"Error retrieving worldview context: {e}")
        
        # Get curriculum-specific context
        if self.curriculum_db:
            try:
                curriculum_results = self.curriculum_db.similarity_search(query, k=3)
                context["curriculum"] = [doc.page_content for doc in curriculum_results]
            except Exception as e:
                print(f"Error retrieving curriculum context: {e}")
        
        # Get relevant Scripture
        if self.scripture_db:
            try:
                scripture_results = self.scripture_db.similarity_search(query, k=1)
                context["scripture"] = [doc.page_content for doc in scripture_results]
            except Exception as e:
                print(f"Error retrieving scripture context: {e}")
        
        return context
#!/usr/bin/env python3
"""
ML Worker для обработки задач из RabbitMQ
С реальной ML моделью на базе scikit-learn
"""

import sys
import os
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import numpy as np
import joblib

# Добавляем путь к проекту для импорта общих модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pika
from app.core.config import settings
from app.models.enums import TaskStatus
from app.queue.rabbitmq import RabbitMQClient

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(f"worker-{os.getpid()}")

class MLWorker:
    """ML воркер для обработки задач с реальной ML моделью"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.client = RabbitMQClient()
        self.models = {}  # Кеш загруженных моделей
        logger.info(f"🚀 Worker {self.worker_id} инициализирован")
    
    def load_model(self, model_id: str):
        """Загрузка ML модели по ID"""
        # Проверяем кеш
        if model_id in self.models:
            return self.models[model_id]
        
        try:
            # Создаем модели на основе ID
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LinearRegression
            from sklearn.cluster import KMeans
            
            if model_id in ['a3c51fb0-f268-441e-a00b-73878c8c5084']:  # Text Classifier
                model = RandomForestClassifier(n_estimators=10, random_state=42)
                X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]])
                y_train = np.array([0, 1, 0, 1, 0, 1])
                model.fit(X_train, y_train)
                
            elif model_id in ['d69bd255-2d3c-4983-82bd-1e562cd8ff8a']:  # Price Predictor
                model = LinearRegression()
                X_train = np.array([[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]])
                y_train = np.array([8, 13, 18, 23, 28])  # 2*x1 + 3*x2
                model.fit(X_train, y_train)
                
            elif model_id in ['e4ee9cc0-ffbd-410c-9034-202194d3f4a4']:  # Customer Clusterer
                model = KMeans(n_clusters=2, random_state=42)
                X_train = np.array([[1, 2], [2, 3], [8, 9], [9, 10], [1.5, 2.5], [8.5, 9.5]])
                model.fit(X_train)
            else:
                raise ValueError(f"Unknown model ID: {model_id}")
            
            self.models[model_id] = model
            logger.info(f"✅ Модель {model_id[:8]}... загружена")
            return model
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки модели {model_id[:8]}...: {e}")
            return None
    
    def validate_features(self, features: Dict[str, Any], model_id: str) -> bool:
        """Валидация входных данных"""
        required = ["x1", "x2"]
        for field in required:
            if field not in features:
                logger.warning(f"❌ Отсутствует поле: {field}")
                return False
        return True
    
    def predict(self, model_id: str, features: Dict[str, Any]) -> Any:
        """Реальное ML предсказание"""
        model = self.load_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id[:8]}... not available")
        
        x1 = float(features.get("x1", 0))
        x2 = float(features.get("x2", 0))
        X = np.array([[x1, x2]])
        
        if hasattr(model, "predict_proba"):
            prediction = model.predict_proba(X).tolist()
        elif hasattr(model, "predict"):
            prediction = model.predict(X).tolist()
        else:
            prediction = model.predict(X).tolist()
        
        logger.info(f"📊 Предсказание: {prediction}")
        return prediction
    
    def process_message(self, message: Dict[str, Any]):
        """Обработка одного сообщения"""
        logger.info(f"📥 Worker {self.worker_id} обрабатывает задачу: {message.get('task_id')[:8]}...")
        
        task_id = message.get("task_id")
        model_id = message.get("model_id")
        features = message.get("features", {})
        
        if not self.validate_features(features, model_id):
            logger.error(f"❌ Ошибка валидации: task={task_id[:8]}...")
            return
        
        try:
            prediction = self.predict(model_id, features)
            logger.info(f"✅ Worker {self.worker_id} завершил задачу: {task_id[:8]}...")
        except Exception as e:
            logger.error(f"❌ Ошибка обработки: {e}")
    
    def run(self):
        """Запуск воркера"""
        logger.info(f"▶️ Worker {self.worker_id} запущен, ожидание задач...")
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.process_message(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"❌ Ошибка обработки сообщения: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        if self.client.connect():
            self.client.channel.basic_qos(prefetch_count=1)
            self.client.channel.basic_consume(
                queue=self.client.queue,
                on_message_callback=callback
            )
            try:
                self.client.channel.start_consuming()
            except KeyboardInterrupt:
                logger.info("🛑 Воркер остановлен")
            finally:
                self.client.close()
        else:
            logger.error("❌ Не удалось подключиться к RabbitMQ")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='ML Worker')
    parser.add_argument('--id', type=str, default=f"worker-{uuid.uuid4().hex[:6]}")
    args = parser.parse_args()
    
    worker = MLWorker(args.id)
    worker.run()

if __name__ == "__main__":
    main()

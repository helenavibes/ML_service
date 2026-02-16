#!/usr/bin/env python3
"""
ML Worker для обработки задач из RabbitMQ
"""

import sys
import os
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any

# Добавляем путь к проекту
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
    """ML воркер для обработки задач"""
    
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.client = RabbitMQClient()
        logger.info(f"🚀 Worker {self.worker_id} инициализирован")
    
    def validate_features(self, features: Dict[str, Any]) -> bool:
        """Валидация входных данных"""
        # Простая валидация - проверяем наличие обязательных полей
        required = ["x1", "x2"]
        for field in required:
            if field not in features:
                logger.warning(f"❌ Отсутствует поле: {field}")
                return False
        return True
    
    def predict(self, features: Dict[str, Any]) -> float:
        """ML предсказание (mock)"""
        # Простая линейная модель: y = 2*x1 + 3*x2 + noise
        x1 = features.get("x1", 0)
        x2 = features.get("x2", 0)
        
        # Имитация вычислений
        time.sleep(0.5)  # Искусственная задержка
        
        prediction = 2 * x1 + 3 * x2
        logger.info(f"📊 Предсказание: {prediction}")
        return prediction
    
    def save_result(self, task_id: str, prediction: float) -> bool:
        """Сохранение результата (здесь можно добавить запись в БД)"""
        # TODO: Здесь можно сохранять результат через API или напрямую в БД
        logger.info(f"💾 Результат сохранен: task={task_id}, prediction={prediction}")
        return True
    
    def process_message(self, message: Dict[str, Any]):
        """Обработка одного сообщения"""
        logger.info(f"📥 Worker {self.worker_id} обрабатывает задачу: {message.get('task_id')}")
        
        # Извлекаем данные
        task_id = message.get("task_id")
        model_id = message.get("model_id")
        features = message.get("features", {})
        timestamp = message.get("timestamp")
        
        # Валидация
        if not self.validate_features(features):
            logger.error(f"❌ Ошибка валидации: task={task_id}")
            # TODO: Обновить статус задачи в БД
            return
        
        # Выполняем предсказание
        try:
            prediction = self.predict(features)
            
            # Сохраняем результат
            self.save_result(task_id, prediction)
            
            # TODO: Обновить статус задачи в БД на COMPLETED
            
            logger.info(f"✅ Worker {self.worker_id} завершил задачу: {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки: {e}")
            # TODO: Обновить статус задачи в БД на FAILED
    
    def run(self):
        """Запуск воркера"""
        logger.info(f"▶️ Worker {self.worker_id} запущен, ожидание задач...")
        
        def callback(ch, method, properties, body):
            """Обработчик сообщений из очереди"""
            try:
                message = json.loads(body)
                self.process_message(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"❌ Ошибка обработки сообщения: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        # Подключаемся и запускаем потребление
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
    """Точка входа"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ML Worker')
    parser.add_argument('--id', type=str, default=f"worker-{uuid.uuid4().hex[:6]}",
                       help='ID воркера')
    
    args = parser.parse_args()
    
    worker = MLWorker(args.id)
    worker.run()

if __name__ == "__main__":
    main()

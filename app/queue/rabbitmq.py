import json
import pika
import logging
from typing import Callable, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """Клиент для работы с RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.url = settings.get_rabbitmq_url()
        self.queue = settings.RABBITMQ_QUEUE
        
    def connect(self):
        """Подключение к RabbitMQ"""
        try:
            params = pika.URLParameters(self.url)
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # Декларируем очередь (создаст если нет)
            self.channel.queue_declare(queue=self.queue, durable=True)
            logger.info(f"✅ Подключено к RabbitMQ, очередь: {self.queue}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к RabbitMQ: {e}")
            return False
    
    def publish(self, message: Dict[str, Any]) -> bool:
        """Публикация сообщения в очередь"""
        if not self.channel:
            if not self.connect():
                return False
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Сохранять сообщение на диске
                )
            )
            logger.info(f"✅ Сообщение опубликовано: {message.get('task_id')}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка публикации: {e}")
            return False
    
    def consume(self, callback: Callable, prefetch_count: int = 1):
        """Запуск потребителя сообщений"""
        if not self.channel:
            if not self.connect():
                return
        
        # Не отдавать новое сообщение, пока не подтверждено предыдущее
        self.channel.basic_qos(prefetch_count=prefetch_count)
        
        def wrapped_callback(ch, method, properties, body):
            """Обертка для обработки сообщения"""
            try:
                message = json.loads(body)
                logger.info(f"📥 Получено сообщение: {message.get('task_id')}")
                callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"✅ Сообщение обработано: {message.get('task_id')}")
            except Exception as e:
                logger.error(f"❌ Ошибка обработки: {e}")
                # Отклоняем и не возвращаем в очередь
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=wrapped_callback
        )
        
        logger.info("👂 Ожидание сообщений. Для выхода нажмите CTRL+C")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        finally:
            self.close()
    
    def close(self):
        """Закрытие соединения"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("🔌 Соединение с RabbitMQ закрыто")

# Синглтон для использования в API
rabbitmq_client = RabbitMQClient()

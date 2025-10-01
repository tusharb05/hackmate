resource "local_file" "ansible_inventory" {
  filename = "${path.module}/inventory.ini"

  content = <<EOT
[user-service]
worker_user ansible_host=${aws_instance.web[0].public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=ssh-key.pem

[team-service]
worker_team ansible_host=${aws_instance.web[1].public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=ssh-key.pem

[notification-service]
worker_notif ansible_host=${aws_instance.web[2].public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=ssh-key.pem

[rabbitmq]
worker_rabbitmq ansible_host=${aws_instance.web[3].public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=ssh-key.pem

[bastion]
bastion ansible_host=${aws_instance.bastion.public_ip} ansible_user=ubuntu ansible_ssh_private_key_file=ssh-key.pem
EOT
}

"""
Módulo contendo arquiteturas de modelos para detecção de alagamentos.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from torchvision.models import ResNet50_Weights, EfficientNet_B0_Weights, VGG16_Weights


class SimpleCNN(nn.Module):
    """
    Rede neural convolucional simples para classificação binária.
    """

    def __init__(self, num_classes=2, dropout_rate=0.5):
        super(SimpleCNN, self).__init__()

        # Camadas convolucionais
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)

        # Normalização em batch
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(128)
        self.bn4 = nn.BatchNorm2d(256)

        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((7, 7))

        # Camadas totalmente conectadas
        self.dropout = nn.Dropout(dropout_rate)
        self.fc1 = nn.Linear(256 * 7 * 7, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        # Primeira convolução
        x = self.pool(F.relu(self.bn1(self.conv1(x))))

        # Segunda convolução
        x = self.pool(F.relu(self.bn2(self.conv2(x))))

        # Terceira convolução
        x = self.pool(F.relu(self.bn3(self.conv3(x))))

        # Quarta convolução
        x = self.pool(F.relu(self.bn4(self.conv4(x))))

        # Pooling adaptativo
        x = self.adaptive_pool(x)

        # Flatten
        x = x.view(x.size(0), -1)

        # Camadas FC
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.dropout(F.relu(self.fc2(x)))
        x = self.fc3(x)

        return x


class ResNetFloodDetector(nn.Module):
    """
    Modelo baseado em ResNet50 com transfer learning.
    """

    def __init__(self, num_classes=2, pretrained=True, freeze_features=False):
        super(ResNetFloodDetector, self).__init__()

        # Carrega ResNet50 pré-treinado
        if pretrained:
            self.backbone = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        else:
            self.backbone = models.resnet50(weights=None)

        # Congela features se especificado
        if freeze_features:
            for param in self.backbone.parameters():
                param.requires_grad = False

        # Substitui a última camada
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


class EfficientNetFloodDetector(nn.Module):
    """
    Modelo baseado em EfficientNet-B0 com transfer learning.
    """

    def __init__(self, num_classes=2, pretrained=True, freeze_features=False):
        super(EfficientNetFloodDetector, self).__init__()

        # Carrega EfficientNet-B0 pré-treinado
        if pretrained:
            self.backbone = models.efficientnet_b0(
                weights=EfficientNet_B0_Weights.IMAGENET1K_V1
            )
        else:
            self.backbone = models.efficientnet_b0(weights=None)

        # Congela features se especificado
        if freeze_features:
            for param in self.backbone.features.parameters():
                param.requires_grad = False

        # Substitui o classificador
        num_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


class VGGFloodDetector(nn.Module):
    """
    Modelo baseado em VGG16 com transfer learning.
    """

    def __init__(self, num_classes=2, pretrained=True, freeze_features=False):
        super(VGGFloodDetector, self).__init__()

        # Carrega VGG16 pré-treinado
        if pretrained:
            self.backbone = models.vgg16(weights=VGG16_Weights.IMAGENET1K_V1)
        else:
            self.backbone = models.vgg16(weights=None)

        # Congela features se especificado
        if freeze_features:
            for param in self.backbone.features.parameters():
                param.requires_grad = False

        # Substitui o classificador
        self.backbone.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(4096, 1024),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(1024, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


class AttentionFloodDetector(nn.Module):
    """
    Modelo com mecanismo de atenção para focar em regiões importantes.
    """

    def __init__(self, num_classes=2, pretrained=True):
        super(AttentionFloodDetector, self).__init__()

        # Backbone ResNet50
        if pretrained:
            backbone = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
        else:
            backbone = models.resnet50(weights=None)

        # Remove a camada FC e pooling
        self.features = nn.Sequential(*list(backbone.children())[:-2])

        # Mecanismo de atenção
        self.attention = nn.Sequential(
            nn.Conv2d(2048, 512, kernel_size=1),
            nn.ReLU(),
            nn.Conv2d(512, 1, kernel_size=1),
            nn.Sigmoid(),
        )

        # Classificador
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(2048, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        # Extrai features
        features = self.features(x)  # [batch, 2048, 7, 7]

        # Calcula mapa de atenção
        attention_map = self.attention(features)  # [batch, 1, 7, 7]

        # Aplica atenção
        attended_features = features * attention_map  # Broadcasting

        # Classifica
        output = self.classifier(attended_features)

        return output, attention_map


def get_model(
    model_name="resnet50", num_classes=2, pretrained=True, freeze_features=False
):
    """
    Factory function para criar modelos.

    Args:
        model_name (str): Nome do modelo ('simple_cnn', 'resnet50', 'efficientnet', 'vgg16', 'attention')
        num_classes (int): Número de classes
        pretrained (bool): Se deve usar pesos pré-treinados
        freeze_features (bool): Se deve congelar as features

    Returns:
        torch.nn.Module: Modelo instanciado
    """

    model_name = model_name.lower()

    if model_name == "simple_cnn":
        model = SimpleCNN(num_classes=num_classes)
    elif model_name == "resnet50":
        model = ResNetFloodDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_features=freeze_features,
        )
    elif model_name == "efficientnet":
        model = EfficientNetFloodDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_features=freeze_features,
        )
    elif model_name == "vgg16":
        model = VGGFloodDetector(
            num_classes=num_classes,
            pretrained=pretrained,
            freeze_features=freeze_features,
        )
    elif model_name == "attention":
        model = AttentionFloodDetector(num_classes=num_classes, pretrained=pretrained)
    else:
        raise ValueError(
            f"Modelo '{model_name}' não reconhecido. "
            f"Opções: 'simple_cnn', 'resnet50', 'efficientnet', 'vgg16', 'attention'"
        )

    return model


def count_parameters(model):
    """
    Conta o número de parâmetros treináveis no modelo.

    Args:
        model (torch.nn.Module): Modelo

    Returns:
        tuple: (total_params, trainable_params)
    """

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    return total_params, trainable_params


def model_summary(model, input_size=(3, 224, 224)):
    """
    Imprime resumo do modelo.

    Args:
        model (torch.nn.Module): Modelo
        input_size (tuple): Tamanho da entrada (C, H, W)
    """

    total_params, trainable_params = count_parameters(model)

    print("=" * 60)
    print(f"Modelo: {model.__class__.__name__}")
    print("=" * 60)
    print(f"Parâmetros totais: {total_params:,}")
    print(f"Parâmetros treináveis: {trainable_params:,}")
    print(f"Parâmetros congelados: {total_params - trainable_params:,}")
    print(f"Tamanho da entrada: {input_size}")

    # Teste de forward pass
    device = next(model.parameters()).device
    dummy_input = torch.randn(1, *input_size).to(device)

    try:
        with torch.no_grad():
            output = model(dummy_input)
            if isinstance(output, tuple):
                output_shape = output[0].shape
                print(f"Formato da saída: {output_shape}")
                if len(output) > 1:
                    print(f"Formato do mapa de atenção: {output[1].shape}")
            else:
                print(f"Formato da saída: {output.shape}")
    except Exception as e:
        print(f"Erro no forward pass: {e}")

    print("=" * 60)


if __name__ == "__main__":
    # Teste dos modelos
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Usando device: {device}")

    models_to_test = ["simple_cnn", "resnet50", "efficientnet", "vgg16", "attention"]

    for model_name in models_to_test:
        print(f"\n\nTestando modelo: {model_name}")
        try:
            model = get_model(model_name, num_classes=2, pretrained=True)
            model = model.to(device)
            model_summary(model)
        except Exception as e:
            print(f"Erro ao testar {model_name}: {e}")

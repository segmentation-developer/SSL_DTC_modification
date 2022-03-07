import os
import argparse
import torch
#from networks.vnet_sdf import VNet
from test_util_VnetandUnet_add import test_all_case
#from networks.vnet_sdf import VNet
#from networks.attentionNet import AttU_Net
#from networks.unet3D import unet_3D
#from networks.attention_Unet3D import Attention_UNet
from networks.vnet import VNet
from networks.unet3D import unet_3D


print(torch.cuda.is_available())
parser = argparse.ArgumentParser()
parser.add_argument('--root_path', type=str,
                    default='/data/sohui/LA_dataset/2018LA_Seg_TrainingSet', help='Name of Experiment')
parser.add_argument('--model', type=str,
                    default='LA/SSL_DTC_VNetandUnet_add', help='model_name')
parser.add_argument('--gpu', type=str,  default='5', help='GPU to use')
parser.add_argument('--detail', type=int,  default=1,
                    help='print metrics for every samples?')
parser.add_argument('--nms', type=int, default=1,
                    help='apply NMS post-procssing?')


FLAGS = parser.parse_args()

os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu
#snapshot_path = "../model/{}".format(FLAGS.model)
snapshot_path = "/home/sohui/code/DTC/model/{}".format(FLAGS.model)

num_classes = 2

test_save_path = os.path.join(snapshot_path, "test/")
if not os.path.exists(test_save_path):
    os.makedirs(test_save_path)
print(test_save_path)
with open(FLAGS.root_path + '/test.list', 'r') as f:
    image_list = f.readlines()
image_list = [FLAGS.root_path + "/" + item.replace('\n', '') + "/mri_norm2.h5" for item in
              image_list]


def test_calculate_metric():
    net1 = VNet(n_channels=1, n_classes=num_classes-1,
                   normalization='batchnorm', has_dropout=True).cuda()
    net2 = unet_3D(in_channels=1, n_classes=1).cuda()
    #save_mode_path = os.path.join(
    #    snapshot_path, 'best_model.pth')
    save_mode_path1 = os.path.join(snapshot_path, 'model1_iter_6000.pth')
    save_mode_path2 = os.path.join(snapshot_path, 'model2_iter_6000.pth')
    net1.load_state_dict(torch.load(save_mode_path1))
    net2.load_state_dict(torch.load(save_mode_path2))

    #print("init weight from {}".format(save_mode_path1))
    net1.eval()
    net2.eval()
    avg_metric = test_all_case([net1,net2], image_list, num_classes=num_classes - 1,
                                patch_size=(112, 112, 80), stride_xy=18, stride_z=4,
                                save_result=True, test_save_path=test_save_path,
                                metric_detail=FLAGS.detail, nms=FLAGS.nms)




    return avg_metric


if __name__ == '__main__':
    metric = test_calculate_metric()  # 6000
    print(metric)

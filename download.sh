#download epi_data
mkdir epi_data/
cd epidata/
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/epi_genetic/selected_tracks.tar.gz
tar -xzf selected_tracks.tar.gz
cd ..
#download weight
mkdir weights/
cd weights/
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_1th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_2th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_3th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_4th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_5th.pth

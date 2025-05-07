#download epi_data
mkdir epi_data/
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/epi_genetic/selected_tracks.tar.gz
tar -xzf selected_tracks.tar.gz
mv *.bigWig epi_data/
#download weight
mkdir weights/
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_1th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_2th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_3th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_4th.pth
wget https://publicphoenixchen.s3.us-east-1.amazonaws.com/weights/best_model_5th.pth
mv *.pth weights/
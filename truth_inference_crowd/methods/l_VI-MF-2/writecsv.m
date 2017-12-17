function [ ret ] = writecsv( filename, Q, K )
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
fid = fopen(filename, 'w');
for i = 1:length(Q)
    fprintf(fid, '%s,%f,%f\n', Q{i}, K(1, i), K(2, i));  % -1 --> 2(here) --> 1 (real)
end
fclose(fid);
ret = 0;
end

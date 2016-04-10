import random
import copy

class Player5:
        """201401191 201401197 copyrighted heuristic approach"""
        def __init__(self):
                self.DEbug = False
                self.printMove = True
                self.useDynaDepth = False

                self.validBlocks= [[0 for i in range(3)] for j in range(3)] 
                self.validBlocks[0][0]=((1,0),(0, 1))
                self.validBlocks[0][1]=((0,0),(0, 2))
                self.validBlocks[0][2]=((0,1),(1, 2))
                self.validBlocks[1][0]=((0,0),(2, 0))
                self.validBlocks[1][1]=((1,1),)
                self.validBlocks[1][2]=((0,2),(2, 2))
                self.validBlocks[2][0]=((1, 0),(2, 1))
                self.validBlocks[2][1]=((2,0),(2, 2))
                self.validBlocks[2][2]=((2,1),(1, 2))
                self.allList = ((0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2))
                self.heuristicDict={}

                #free time for computations!!!!
                self.getBlockScore([[0]*3 for i in range(3)])

        def checkAllowedBlocks(self, prevMove, BlockStatus):
                if prevMove[0] < 0 and prevMove[1] < 0:
                        return self.allList
                allowedBlocks = self.validBlocks[prevMove[0]%3][prevMove[1]%3]
                finalAllowedBlocks = []
                for i in allowedBlocks:
                        if BlockStatus[i[0]][i[1]] == 0:
                                finalAllowedBlocks.append(i)
                if len(finalAllowedBlocks)==0:
                        for i in self.allList:
                                if BlockStatus[i[0]][i[1]] == 0:
                                        finalAllowedBlocks.append(i)
                return finalAllowedBlocks

        def checkAllowedMarkers(self,block):
                allowed=[]
                for i in range(3):
                        for j in range(3):
                                if block[i][j] == 0:
                                        allowed.append((i, j))
                return allowed

        def getAllowedMoves(self, currentBoard, currentBlockStatus, prevMove):
                moveList=[]
                for allowedBlock in self.checkAllowedBlocks(prevMove, currentBlockStatus):
                        moveList += [(3*allowedBlock[0]+move[0], 3*allowedBlock[1]+move[1]) for move in self.checkAllowedMarkers(currentBoard[allowedBlock[0]][allowedBlock[1]])]
                return moveList

        def getBlockStatus(self, block):
                #check rows and columns
                for i in range(3):
                        if block[i][0]==block[i][1]==block[i][2] and block[i][1] in (1,2):
                                return block[i][1]
                        if block[0][i]==block[1][i]==block[2][i] and block[1][i] in (1,2):
                                return block[1][i]
                #check diagonals
                if block[0][0]==block[1][1]==block[2][2] and block[1][1] in (1,2):
                        return block[1][1]
                if block[0][2]==block[1][1]==block[2][0] and block[1][1] in (1,2):
                        return block[1][1]
                #draw check
                if not len(self.checkAllowedMarkers(block)):
                        return 3
                return 0

        def getBlockScore(self, block):
                block = tuple([tuple(block[i]) for i in range(3)])
                if block not in self.heuristicDict:
                        blockStat = self.getBlockStatus(block)
                        if blockStat == 1:
                                self.heuristicDict[block] = 1.0
                        elif blockStat in (2,3):
                                self.heuristicDict[block] = 0.0
                        else:
                                moves = self.checkAllowedMarkers(block)
                                #we play the next move
                                wePlayList = []
                                playBlock = [list(block[i]) for i in range(3)]
                                for move in moves:
                                        playBlock[move[0]][move[1]] = 1
                                        wePlayList.append(self.getBlockScore(playBlock))
                                        playBlock[move[0]][move[1]] = 0
                                #opponent plays the next move
                                theyPlayList = []
                                for move in moves:
                                        playBlock[move[0]][move[1]] = 2
                                        theyPlayList.append(self.getBlockScore(playBlock))
                                        playBlock[move[0]][move[1]] = 0
                                self.heuristicDict[block] = 0.5*(max(wePlayList)+min(theyPlayList))
                return self.heuristicDict[block]

        def lineScore(self, line, blockProb, revBlockProb, currentBlockStatus):
                if 3 in [currentBlockStatus[x[0]][x[1]] for x in line]:
                        return 0
                positiveScore = [blockProb[x[0]][x[1]] for x in line]
                negativeScore = [revBlockProb[x[0]][x[1]] for x in line]
                return positiveScore[0]*positiveScore[1]*positiveScore[2]-negativeScore[0]*negativeScore[1]*negativeScore[2]
                
        def getBoardScore(self, currentBoard, currentBlockStatus):
                terminalStat, terminalScore = self.terminalCheck(currentBoard, currentBlockStatus)
                if terminalStat:
                        return terminalScore
                revCurrentBoard = copy.deepcopy(currentBoard)
                for r in range(3):
                        for c in range(3):
                                for i in range(3):
                                        for j in range(3):
                                                if revCurrentBoard[r][c][i][j]:
                                                        revCurrentBoard[r][c][i][j] = 3 - revCurrentBoard[r][c][i][j]
                blockProb=[[0]*3 for i in range(3)]
                revBlockProb=[[0]*3 for i in range(3)]
                for i in range(3):
                        for j in range(3):
                                blockProb[i][j] = self.getBlockScore(currentBoard[i][j])
                                revBlockProb[i][j] = self.getBlockScore(revCurrentBoard[i][j])
                boardScore = []
                for i in range(3):
                        line = [(i,j) for j in range(3)]
                        boardScore.append(self.lineScore(line, blockProb, revBlockProb, currentBlockStatus))
                        line = [(j,i) for j in range(3)]
                        boardScore.append(self.lineScore(line, blockProb, revBlockProb, currentBlockStatus))
                line = [(i,i) for i in range(3)]
                boardScore.append(self.lineScore(line, blockProb, revBlockProb, currentBlockStatus))
                line = [(i,2-i) for i in range(3)]
                boardScore.append(self.lineScore(line, blockProb, revBlockProb, currentBlockStatus))
                if 1 in boardScore:
                        print "found win", currentBoard
                        return 100
                elif -1 in boardScore:
                        return -100
                return sum(boardScore)

        def move(self, currentBoard, currentBlockStatus, oldMove, flag):
                # new 3*3*3*3 array for board
                formattedBoard = [[[[0]*3 for i in range(3)] for j in range(3)] for j in range(3)]
                # new 3*3 array for block status
                formattedBlockStatus = [[0]*3 for i in range(3)]

                # copy data to formattedBoard
                for i in range(9):
                        for j in range(9):
                                if currentBoard[i][j] == flag:
                                        formattedBoard[i/3][j/3][i%3][j%3] = 1
                                elif currentBoard[i][j] == '-':
                                        formattedBoard[i/3][j/3][i%3][j%3] = 0
                                else:
                                        formattedBoard[i/3][j/3][i%3][j%3] = 2

                # copy data to formattedBlockStatus
                for i in range(3):
                        for j in range(3):
                                if currentBlockStatus[i*3+j] == flag:
                                        formattedBlockStatus[i][j] = 1
                                elif currentBlockStatus[i*3+j] == '-':
                                        formattedBlockStatus[i][j] = 0
                                elif currentBlockStatus[i*3+j] == 'D':
                                        formattedBlockStatus[i][j] = 3
                                else:
                                        formattedBlockStatus[i][j] = 2

                if oldMove[0] < 0 or oldMove[1] < 0:
                        uselessScore, nextMove, retDepth = 0, (3, 3), 0
                        depth = 0
                else:
                        if self.useDynaDepth:
                                try:
                                        possiBranch = [len(self.checkAllowedMarkers(formattedBoard[i][j])) for i in range(3) for j in range(3) if formattedBlockStatus[i][j] == 0]
                                        possiBranch.sort()
                                        branch = sum(possiBranch[-2:])
                                except:
                                        branch = 18
                                if branch <= 3:
                                        depth = 12
                                elif branch <= 4:
                                        depth = 9
                                elif branch <= 5:
                                        depth = 8
                                elif branch <= 7:
                                        depth = 7
                                elif branch <= 10:
                                        depth = 6
                                else:
                                        depth = 5
                        else:
                                depth = 5
                        uselessScore, nextMove, retDepth = self.alphaBetaPruning(formattedBoard, formattedBlockStatus, -100000000, 100000000, True, oldMove, depth)
                if self.DEbug or self.printMove:
                        print "move", nextMove, uselessScore, retDepth, depth
                return nextMove

        def terminalCheck(self, currentBoard, currentBlockStatus):
                terminalStat = self.getBlockStatus(currentBlockStatus)
                if terminalStat == 0:
                        return (False, 0)
                elif terminalStat == 1:
                        return (True, 100)
                elif terminalStat == 2:
                        return (True, -100)
                else:
                        blockCount = 0
                        midCount = 0
                        for i in range(3):
                                for j in range(3):
                                        if currentBlockStatus[i][j] in (1,2):
                                                blockCount += 3-2*currentBlockStatus[i][j]
                                        if currentBoard[i][j][1][1] in (1,2):
                                                midCount += 3-2*currentBoard[i][j][1][1]

                        if blockCount > 0:
                                return (True, 1)
                        elif blockCount < 0:
                                return (True, -1)
                        elif midCount > 0:
                                return (True, 1)
                        elif midCount < 0:
                                return (True, -1)
                        else:
                                return (True, 0)


        def alphaBetaPruning(self, currentBoard, currentBlockStatus, alpha, beta, flag, prevMove, depth):
                #make a copy of lists

                tempBoard = copy.deepcopy(currentBoard)
                tempBlockStatus = copy.deepcopy(currentBlockStatus)
                terminalStat, terminalScore = self.terminalCheck(currentBoard, currentBlockStatus)
                if terminalStat:
                        if self.DEbug:
                            print "Reached terminal state",prevMove,terminalScore  
                        return terminalScore, (), 0
                if depth<=0:
                        return self.getBoardScore(currentBoard, currentBlockStatus), (), 0

                possibMoves = self.getAllowedMoves(currentBoard, currentBlockStatus, prevMove)
                random.shuffle(possibMoves)
                if self.DEbug:
                    print "ab",prevMove,flag,depth,possibMoves
                bestMove = ()
                bestDepth = 100
                if flag:
                        v = -100000000
                        for move in possibMoves:
                                #implement the move
                                tempBoard[move[0]/3][move[1]/3][move[0]%3][move[1]%3] = 1
                                tempBlockStatus[move[0]/3][move[1]/3] = self.getBlockStatus(tempBoard[move[0]/3][move[1]/3])

                                childScore, childBest, childDepth = self.alphaBetaPruning(tempBoard, tempBlockStatus, alpha, beta, not flag, move, depth-1)
                                if childScore >= v:
                                        if v < childScore or bestDepth > childDepth:
                                                v = childScore
                                                bestMove = move
                                                bestDepth = childDepth
                                alpha = max(alpha, v)

                                #revert the implemented move
                                tempBoard[move[0]/3][move[1]/3][move[0]%3][move[1]%3] = 0
                                tempBlockStatus[move[0]/3][move[1]/3] = self.getBlockStatus(tempBoard[move[0]/3][move[1]/3])

                                if alpha >= beta:
                                        break
                        if self.DEbug:
                            print "ret",prevMove,depth,v,bestMove
                        return v, bestMove, bestDepth+1
                else:
                        v = 100000000
                        for move in possibMoves:
                                #implement the move
                                tempBoard[move[0]/3][move[1]/3][move[0]%3][move[1]%3] = 2
                                tempBlockStatus[move[0]/3][move[1]/3] = self.getBlockStatus(tempBoard[move[0]/3][move[1]/3])

                                childScore, childBest, childDepth = self.alphaBetaPruning(tempBoard, tempBlockStatus, alpha, beta, not flag, move, depth-1)
                                if childScore <= v:
                                        if v > childScore or bestDepth > childDepth:
                                                v = childScore
                                                bestMove = move
                                                bestDepth = childDepth
                                beta = min(beta, v)

                                #revert the implemented move
                                tempBoard[move[0]/3][move[1]/3][move[0]%3][move[1]%3] = 0
                                tempBlockStatus[move[0]/3][move[1]/3] = self.getBlockStatus(tempBoard[move[0]/3][move[1]/3])

                                if alpha >= beta:
                                        break
                        if self.DEbug:
                            print "ret",prevMove,depth,v,bestMove
                        return v, bestMove, bestDepth+1
